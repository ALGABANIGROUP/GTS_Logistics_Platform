# PowerShell script to move all TMS-related frontend files to trash folder
$src = "d:\GTS\frontend\src"
$dst = "d:\GTS\_trash_TMS_20260116"

# Move pages/tms
Move-Item "$src\pages\tms" $dst -Force
# Move components/tms
Move-Item "$src\components\tms" $dst -Force
# Move styles/tms.css and tms-map.css
Move-Item "$src\styles\tms.css" $dst -Force
Move-Item "$src\styles\tms-map.css" $dst -Force
# Move utils/tms
Move-Item "$src\utils\tms" $dst -Force
