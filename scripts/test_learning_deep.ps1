param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$Username = "",
  [string]$Password = "",
  [string]$Token = ""
)

$ErrorActionPreference = "Stop"

function Write-Section {
  param([string]$Title)
  Write-Host ""
  Write-Host ("=" * 72) -ForegroundColor DarkGray
  Write-Host $Title -ForegroundColor Cyan
  Write-Host ("=" * 72) -ForegroundColor DarkGray
}

function Write-Pass {
  param([string]$Message)
  Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Write-Fail {
  param([string]$Message)
  Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Write-Info {
  param([string]$Message)
  Write-Host "[INFO] $Message" -ForegroundColor Yellow
}

function Write-Stat {
  param([string]$Label, $Value, [string]$Change = "")
  $changeText = if ($Change) { $Change } else { "" }
  Write-Host ("  - {0,-32} {1,-18} {2}" -f $Label, $Value, $changeText) -ForegroundColor White
}

function Invoke-JsonGet {
  param(
    [string]$Url,
    [hashtable]$Headers = @{}
  )
  return Invoke-RestMethod -Method Get -Uri $Url -Headers $Headers
}

function Invoke-JsonPost {
  param(
    [string]$Url,
    [object]$Body,
    [hashtable]$Headers = @{}
  )
  $jsonBody = $Body | ConvertTo-Json -Depth 10
  $localHeaders = @{}
  foreach ($k in $Headers.Keys) {
    $localHeaders[$k] = $Headers[$k]
  }
  $localHeaders["Content-Type"] = "application/json"
  return Invoke-RestMethod -Method Post -Uri $Url -Headers $localHeaders -Body $jsonBody
}

function Get-BotStats {
  param(
    [object]$LearningStats,
    [string]$BotId
  )

  if ($LearningStats -and $LearningStats.per_bot -and $LearningStats.per_bot.PSObject.Properties.Name -contains $BotId) {
    return $LearningStats.per_bot.$BotId
  }
  return $null
}

function Get-ValueOrDefault {
  param(
    $Value,
    $Default = 0
  )

  if ($null -eq $Value) {
    return $Default
  }
  return $Value
}

Write-Section "Authentication"

if (-not $Token) {
  if (-not $Username -or -not $Password) {
    throw "Provide -Token or both -Username and -Password."
  }

  $authBody = "username=$([uri]::EscapeDataString($Username))&password=$([uri]::EscapeDataString($Password))"
  $authResponse = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/v1/auth/token" `
    -ContentType "application/x-www-form-urlencoded" `
    -Body $authBody

  if (-not $authResponse.access_token) {
    throw "No access token returned."
  }

  $Token = [string]$authResponse.access_token
  Write-Pass "Access token acquired"
}
else {
  Write-Pass "Using provided bearer token"
}

$headers = @{ Authorization = "Bearer $Token" }
$testSessionId = "deep-test-$([guid]::NewGuid().ToString('N'))"

Write-Section "Recording Initial State"

$learningBefore = Invoke-JsonGet -Url "$BaseUrl/ai/learning/stats"
$maintenanceSummaryBefore = Invoke-JsonGet -Url "$BaseUrl/api/v1/maintenance-dev/health-summary"
$maintenanceHistoryBefore = Invoke-JsonGet -Url "$BaseUrl/api/v1/maintenance-dev/history"

$customerBefore = Get-BotStats -LearningStats $learningBefore -BotId "customer_service"
$beforeSamples = [int](Get-ValueOrDefault $learningBefore.total_samples_collected 0)
$beforeAdaptations = [int](Get-ValueOrDefault $learningBefore.total_adaptations 0)
$beforeCustomerSamples = [int](Get-ValueOrDefault $customerBefore.samples 0)
$beforeCustomerAdaptations = [int](Get-ValueOrDefault $customerBefore.adaptations 0)
$beforeRepairEntries = @($maintenanceHistoryBefore.fixed_issues).Count
$beforeRepairAttempts = [int](Get-ValueOrDefault $maintenanceHistoryBefore.repair_attempts 0)
$beforeIssues = [int](Get-ValueOrDefault $maintenanceSummaryBefore.issues_found 0)

Write-Info "Initial state snapshot:"
Write-Stat "total_samples_collected" $beforeSamples
Write-Stat "total_adaptations" $beforeAdaptations
Write-Stat "customer_service.samples" $beforeCustomerSamples
Write-Stat "customer_service.adaptations" $beforeCustomerAdaptations
Write-Stat "maintenance.issues_found" $beforeIssues
Write-Stat "maintenance.repair_entries" $beforeRepairEntries
Write-Stat "maintenance.repair_attempts" $beforeRepairAttempts

Write-Section "Creating A Real Learning Sample"

$feedbackResult = Invoke-JsonPost `
  -Url "$BaseUrl/ai/learning/data/feedback?bot_id=customer_service" `
  -Body @{
    rating = 4
    session_id = $testSessionId
    comment = "Deep verification sample"
    user_id = "deep-test-user"
    feedback_type = "deep_verification"
    tags = @("deep_test", "customer_service")
  }

Write-Pass "Feedback sample recorded for customer_service"
Write-Info ("Feedback API status: {0}" -f (Get-ValueOrDefault $feedbackResult.status "unknown"))

Start-Sleep -Seconds 1

Write-Section "Triggering Manual Learning"

$triggerResult = Invoke-JsonPost -Url "$BaseUrl/ai/learning/trigger/customer_service" -Body @{}
Write-Pass "Learning trigger executed"
Write-Info ("Learning status: {0}" -f (Get-ValueOrDefault $triggerResult.learning_result.status "unknown"))

Start-Sleep -Seconds 2

Write-Section "Running Auto-Repair"

$repairResult = Invoke-JsonPost -Url "$BaseUrl/api/v1/maintenance-dev/auto-repair" -Headers $headers -Body @{}
Write-Pass "Auto-repair executed"

Write-Info "Repair response:"
Write-Stat "issues_found" (Get-ValueOrDefault $repairResult.issues_found 0)
Write-Stat "issues_repaired" (Get-ValueOrDefault $repairResult.issues_repaired 0)
Write-Stat "actions_attempted" (Get-ValueOrDefault $repairResult.actions_attempted 0)
Write-Stat "success_rate" ("{0}%" -f (Get-ValueOrDefault $repairResult.success_rate 0))

Start-Sleep -Seconds 2

Write-Section "Recording Final State"

$learningAfter = Invoke-JsonGet -Url "$BaseUrl/ai/learning/stats"
$maintenanceSummaryAfter = Invoke-JsonGet -Url "$BaseUrl/api/v1/maintenance-dev/health-summary"
$maintenanceHistoryAfter = Invoke-JsonGet -Url "$BaseUrl/api/v1/maintenance-dev/history"

$customerAfter = Get-BotStats -LearningStats $learningAfter -BotId "customer_service"
$afterSamples = [int](Get-ValueOrDefault $learningAfter.total_samples_collected 0)
$afterAdaptations = [int](Get-ValueOrDefault $learningAfter.total_adaptations 0)
$afterCustomerSamples = [int](Get-ValueOrDefault $customerAfter.samples 0)
$afterCustomerAdaptations = [int](Get-ValueOrDefault $customerAfter.adaptations 0)
$afterRepairEntries = @($maintenanceHistoryAfter.fixed_issues).Count
$afterRepairAttempts = [int](Get-ValueOrDefault $maintenanceHistoryAfter.repair_attempts 0)
$afterIssues = [int](Get-ValueOrDefault $maintenanceSummaryAfter.issues_found 0)

$deltaSamples = $afterSamples - $beforeSamples
$deltaAdaptations = $afterAdaptations - $beforeAdaptations
$deltaCustomerSamples = $afterCustomerSamples - $beforeCustomerSamples
$deltaCustomerAdaptations = $afterCustomerAdaptations - $beforeCustomerAdaptations
$deltaRepairEntries = $afterRepairEntries - $beforeRepairEntries
$deltaRepairAttempts = $afterRepairAttempts - $beforeRepairAttempts
$deltaIssues = $afterIssues - $beforeIssues

Write-Info "Final state snapshot:"
Write-Stat "total_samples_collected" $afterSamples ("delta {0:+#;-#;0}" -f $deltaSamples)
Write-Stat "total_adaptations" $afterAdaptations ("delta {0:+#;-#;0}" -f $deltaAdaptations)
Write-Stat "customer_service.samples" $afterCustomerSamples ("delta {0:+#;-#;0}" -f $deltaCustomerSamples)
Write-Stat "customer_service.adaptations" $afterCustomerAdaptations ("delta {0:+#;-#;0}" -f $deltaCustomerAdaptations)
Write-Stat "maintenance.issues_found" $afterIssues ("delta {0:+#;-#;0}" -f $deltaIssues)
Write-Stat "maintenance.repair_entries" $afterRepairEntries ("delta {0:+#;-#;0}" -f $deltaRepairEntries)
Write-Stat "maintenance.repair_attempts" $afterRepairAttempts ("delta {0:+#;-#;0}" -f $deltaRepairAttempts)

Write-Section "Analysis"

$sampleGrowthOk = ($deltaSamples -gt 0) -or ($deltaCustomerSamples -gt 0)
$learningRanOk = ($triggerResult.learning_result.status -eq "success") -or ($triggerResult.learning_result.status -eq "no_data")
$repairRecordedOk = ($deltaRepairEntries -gt 0) -or ((Get-ValueOrDefault $repairResult.actions_attempted 0) -gt 0) -or ($deltaRepairAttempts -gt 0)
$issuesStableOk = ($deltaIssues -le 0)

Write-Info "Learning impact:"
if ($sampleGrowthOk) {
  Write-Pass ("Learning samples increased. Total delta={0}, customer_service delta={1}" -f $deltaSamples, $deltaCustomerSamples)
}
else {
  Write-Fail ("No sample growth detected. Total delta={0}, customer_service delta={1}" -f $deltaSamples, $deltaCustomerSamples)
}

if ($deltaCustomerAdaptations -gt 0 -or $deltaAdaptations -gt 0) {
  Write-Pass ("Adaptations increased. Total delta={0}, customer_service delta={1}" -f $deltaAdaptations, $deltaCustomerAdaptations)
}
else {
  Write-Info "Adaptations unchanged. This is acceptable when there are not enough new patterns."
}

Write-Info "Maintenance impact:"
if ($repairRecordedOk) {
  Write-Pass ("Auto-repair recorded activity. repair_entries delta={0}, repair_attempts delta={1}" -f $deltaRepairEntries, $deltaRepairAttempts)
}
else {
  Write-Fail "Auto-repair did not leave any measurable trace in maintenance history."
}

if ($issuesStableOk) {
  if ($deltaIssues -lt 0) {
    Write-Pass ("Issues decreased by {0}" -f (-$deltaIssues))
  }
  else {
    Write-Info "Issue count remained stable."
  }
}
else {
  Write-Info ("Issue count increased by {0}. This can happen if a fresh scan discovered additional problems." -f $deltaIssues)
}

if ($maintenanceHistoryAfter.last_repair) {
  Write-Info "Latest repair summary:"
  Write-Stat "last_repair.status" (Get-ValueOrDefault $maintenanceHistoryAfter.last_repair.status "unknown")
  Write-Stat "last_repair.issues_repaired" (Get-ValueOrDefault $maintenanceHistoryAfter.last_repair.issues_repaired 0)
  Write-Stat "last_repair.actions_attempted" (Get-ValueOrDefault $maintenanceHistoryAfter.last_repair.actions_attempted 0)
}

Write-Section "Summary"

$deepPass = $learningRanOk -and $sampleGrowthOk -and $repairRecordedOk

if ($deepPass) {
  Write-Pass "Deep learning and auto-repair checks passed"
}
else {
  Write-Fail "Deep checks did not show the expected state changes"
  exit 1
}

Write-Info "Rotate the test account password immediately after testing."
