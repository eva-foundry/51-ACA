$draft = Get-Content "C:\AICOE\eva-foundry\51-ACA\_opus_review_issue_draft.md" -Raw

# Extract title (line after "## TITLE")
$titleMatch = [regex]::Match($draft, '(?m)^## TITLE\r?\n(.+)')
$title = $titleMatch.Groups[1].Value.Trim()

# Extract body (everything after "## BODY\r\n")
$bodyMatch = [regex]::Match($draft, '(?ms)^## BODY\r?\n(.+)')
$body = $bodyMatch.Groups[1].Value.Trim()

# Strip trailing markdown code fence if present
$body = $body -replace '^\s*```\s*$', '' -replace '```\s*$', ''
$body = $body.Trim()

$bodyFile = "$env:TEMP\sonnet-review-body.md"
[System.IO.File]::WriteAllText($bodyFile, $body, [System.Text.Encoding]::UTF8)

Write-Host "[INFO] Title : $title"
Write-Host "[INFO] Body  : $((Get-Content $bodyFile).Count) lines"

gh issue create `
    --repo "eva-foundry/51-ACA" `
    --title $title `
    --label "sonnet-review" `
    --body-file $bodyFile

Write-Host "[PASS] Issue created. EXIT=$LASTEXITCODE"
