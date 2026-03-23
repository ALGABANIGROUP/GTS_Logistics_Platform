$routes = Invoke-RestMethod http://127.0.0.1:8020/_debug/routes
$openapi = Invoke-RestMethod http://127.0.0.1:8020/openapi.json
"{0} routes loaded" -f $routes.count
# verify specific paths
$expected = @("/auth/token","/auth/debug","/finance/summary","/documents/expiring-soon/")
foreach ($p in $expected) {
  if ($routes.routes.path -contains $p) { Write-Host "✅ $p" } else { Write-Warning "⚠️ missing $p" }
}
# check /auth/token body types
$auth = $openapi.paths."/auth/token".post.requestBody.content.Keys
Write-Host ("Auth body content-types: " + ($auth -join ", "))
