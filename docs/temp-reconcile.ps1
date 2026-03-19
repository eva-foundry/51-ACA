$compFile = "C:\eva-foundry\51-ACA\docs\WBS-FROM-DOCS-COMPLETE-20260311.md"
$baseFile = "C:\eva-foundry\51-ACA\docs\archive\PLAN.md"
$gapsFile = "C:\eva-foundry\51-ACA\docs\GAPS-AND-DECISIONS.md"

# Read files
$compLines = Get-Content $compFile
$baseLines = Get-Content $baseFile  
$gapsLines = Get-Content $gapsFile

# Extract comprehensive WBS stories
$compStories = @{}
foreach ($line in $compLines) {
    if ($line -match '^\- \*\*ACA-(\d+)-(\d+)\*\*: (.+)') {
        $epic = $matches[1]
        $num = $matches[2]
        $id = "ACA-$epic-$num"
        $title = $matches[3]
        $compStories[$id] = @{
            id = $id
            title = $title
            epic = $epic
            source = "comprehensive"
        }
    }
}

# Extract baseline stories with status
$baseStories = @{}
$currentEpic = ""
foreach ($i = 0; $i -lt $baseLines.Count; $i++) {
    $line = $baseLines[$i]
    
    # Track epic
    if ($line -match '^EPIC (\d+)') {
        $currentEpic = $matches[1]
    }
    
    # Extract story
    if ($line -match 'Story.*\[ACA-(\d+)-(\d+)\]\s+(.+)') {
        $epic = $matches[1]
        $num = $matches[2]
        $id = "ACA-$epic-$num"
        $title = $matches[3]
        
        # Check next line for status
        $status = "not-started"
        if ($i+1 -lt $baseLines.Count) {
            $nextLine = $baseLines[$i+1]
            if ($nextLine -match 'Status: DONE') {
                $status = "done"
            } elseif ($nextLine -match 'Status: IN[_ ]PROGRESS') {
                $status = "in-progress"
            }
        }
        
        $baseStories[$id] = @{
            id = $id
            title = $title
            epic = $epic
            status = $status
            source = "baseline"
        }
    }
}

# Extract gap stories
$gapStories = @()
if ($gapsLines -match 'ACA-01-022') { $gapStories += "ACA-01-022" }
if ($gapsLines -match 'ACA-02-018') { $gapStories += "ACA-02-018" }
if ($gapsLines -match 'ACA-02-019') { $gapStories += "ACA-02-019" }
if ($gapsLines -match 'ACA-04-029') { $gapStories += "ACA-04-029" }
if ($gapsLines -match 'ACA-11-010') { $gapStories += "ACA-11-010" }

Write-Host "[INFO] Comprehensive WBS: $($compStories.Count) stories"
Write-Host "[INFO] Baseline WBS: $($baseStories.Count) stories"
Write-Host "[INFO] Gap stories: $($gapStories.Count) stories"
Write-Host ""

# Find matches
$matched = 0
$baseline_only = 0  
$comprehensive_only = 0

foreach ($id in $baseStories.Keys) {
    if ($compStories.ContainsKey($id)) {
        $matched++
    } else {
        $baseline_only++
    }
}

$comprehensive_only = $compStories.Count - $matched

Write-Host "[STAT] Matched stories: $matched"
Write-Host "[STAT] Baseline-only stories: $baseline_only"
Write-Host "[STAT] Comprehensive-only (new): $comprehensive_only"

# Save comparison for detailed review
$results = @()
foreach ($id in ($baseStories.Keys + $compStories.Keys | Sort-Object -Unique)) {
    $results += [PSCustomObject]@{
        StoryID = $id
        InBaseline = $baseStories.ContainsKey($id)
        InComprehensive = $compStories.ContainsKey($id)
        Status = if ($baseStories.ContainsKey($id)) { $baseStories[$id].status } else { "n/a" }
        BaselineTitle = if ($baseStories.ContainsKey($id)) { $baseStories[$id].title } else { "" }
        CompTitle = if ($compStories.ContainsKey($id)) { $compStories[$id].title } else { "" }
    }
}

$results | Sort-Object StoryID | Export-Csv "C:\eva-foundry\51-ACA\docs\story-mapping-analysis.csv" -NoTypeInformation
Write-Host "[SAVED] Detailed mapping: C:\eva-foundry\51-ACA\docs\story-mapping-analysis.csv"
