# PowerShell script to move all TMS-related backend files to trash folder
$src = "d:\GTS\backend\tms"
$dst = "d:\GTS\_trash_TMS_20260116"

Move-Item $src $dst -Force
