$plan = Get-Content "C:\eva-foundry\51-ACA\.eva\veritas-plan.json" -Raw | ConvertFrom-Json
$total = 0; $done = 0; $notDone = 0
foreach ($f in $plan.features) {
    $t = $f.stories.Count
    $d = ($f.stories | Where-Object { $_.done -eq $true }).Count
    $nd = $t - $d
    $total += $t; $done += $d; $notDone += $nd
    $title = $f.title
    if ($title.Length -gt 45) { $title = $title.Substring(0,45) + "..." }
    Write-Host ("{0,-8} {1,-48} total={2,3} done={3,3} remain={4,3}" -f $f.id, $title, $t, $d, $nd)
}
Write-Host ""
Write-Host ("TOTAL stories : {0}" -f $total)
Write-Host ("Done          : {0}" -f $done)
Write-Host ("Remaining     : {0}" -f $notDone)
