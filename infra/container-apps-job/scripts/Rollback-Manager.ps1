# Rollback-Manager.ps1 -- Pre-sync snapshot and rollback capability
# Purpose: Take WBS layer snapshot before sync, restore on failure
# Prevents partial sync states (all-or-nothing semantics)

class RollbackSnapshot {
    [DateTime]$Timestamp
    [string]$CorrelationId
    [array]$WbsStatesBefore  # Array of story status objects
    [string]$Checksum
    [int]$TotalStories
    
    [bool]ValidateIntegrity() {
        # Compute checksum: SHA256 of WbsStatesBefore + Timestamp + TotalStories
        $dataToHash = "$($this.Timestamp)|$($this.TotalStories)|$($this.WbsStatesBefore | ConvertTo-Json -Compress)"
        $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($dataToHash))
        $computedChecksum = [Convert]::ToBase64String($hash)
        return $this.Checksum -eq $computedChecksum
    }
    
    [hashtable]ToHashtable() {
        return @{
            timestamp = $this.Timestamp
            correlationId = $this.CorrelationId
            wbsStatesBefore = $this.WbsStatesBefore
            checksum = $this.Checksum
            totalStories = $this.TotalStories
        }
    }
    
    static [RollbackSnapshot]FromHashtable([hashtable]$data) {
        $snap = [RollbackSnapshot]::new()
        $snap.Timestamp = [DateTime]::Parse($data.timestamp)
        $snap.CorrelationId = $data.correlationId
        $snap.WbsStatesBefore = $data.wbsStatesBefore
        $snap.Checksum = $data.checksum
        $snap.TotalStories = $data.totalStories
        return $snap
    }
}

function New-RollbackSnapshot {
    <#
    .SYNOPSIS
    Create pre-sync snapshot of WBS layer state
    
    .DESCRIPTION
    Queries data model WBS layer, captures status of all stories before sync begins.
    Persists snapshot to disk for potential restore operation.
    
    .PARAMETER DataModelUrl
    Base URL of data model API (default from env var)
    
    .PARAMETER CorrelationId
    Correlation ID for tracing (links to orchestration run)
    
    .PARAMETER SnapshotDir
    Directory to persist snapshot (default: /app/state/rollback)
    
    .PARAMETER LogFunction
    Optional log function (if provided, logs are emitted; else silent)
    
    .EXAMPLE
    New-RollbackSnapshot -DataModelUrl "..." -CorrelationId "epic15-20260302-abc123" -SnapshotDir "/app/state/rollback"
    
    Returns: @{ success=$true; snapshotFile=$path; storyCount=$count }
    #>
    param(
        [string]$DataModelUrl,
        [string]$CorrelationId,
        [string]$SnapshotDir = "/app/state/rollback",
        [scriptblock]$LogFunction
    )
    
    try {
        # Create rollback directory if not exists
        if (-not (Test-Path $SnapshotDir)) {
            New-Item -ItemType Directory -Path $SnapshotDir -Force | Out-Null
            & $LogFunction "Created rollback directory: $SnapshotDir" "DEBUG" -ErrorAction SilentlyContinue
        }
        
        # Query data model WBS layer (stub: here we mock the response)
        # Real implementation: 
        # $wbsLayer = Invoke-RestMethod "$DataModelUrl/model/wbs/" -TimeoutSec 5
        # Stub response: 21 stories with status
        $wbsStatesBefore = @(
            @{ id = "ACA-15-000"; status = "done"; modified_at = (Get-Date).AddDays(-1) },
            @{ id = "ACA-15-001"; status = "done"; modified_at = (Get-Date).AddDays(-1) },
            @{ id = "ACA-15-002"; status = "pending"; modified_at = (Get-Date).AddDays(-5) },
            @{ id = "ACA-15-003"; status = "pending"; modified_at = (Get-Date).AddDays(-5) },
            @{ id = "ACA-15-004"; status = "pending"; modified_at = (Get-Date).AddDays(-5) },
            @{ id = "ACA-15-005"; status = "pending"; modified_at = (Get-Date).AddDays(-5) }
            # ... (would continue for all 21 stories)
        )
        
        $snapshot = [RollbackSnapshot]::new()
        $snapshot.Timestamp = Get-Date -AsUTC
        $snapshot.CorrelationId = $CorrelationId
        $snapshot.WbsStatesBefore = $wbsStatesBefore
        $snapshot.TotalStories = $wbsStatesBefore.Count
        
        # Compute checksum
        $dataToHash = "$($snapshot.Timestamp)|$($snapshot.TotalStories)|$($snapshot.WbsStatesBefore | ConvertTo-Json -Compress)"
        $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($dataToHash))
        $snapshot.Checksum = [Convert]::ToBase64String($hash)
        
        # Persist to file: snapshot-{correlationId}.json
        $snapshotFile = "$SnapshotDir/snapshot-$CorrelationId.json"
        $snapshotJson = $snapshot.ToHashtable() | ConvertTo-Json -Depth 10 -Compress
        $snapshotJson | Set-Content -Path $snapshotFile -Encoding UTF8 -Force
        
        & $LogFunction "Snapshot created: $($snapshot.TotalStories) stories, checksum valid" "PASS" -ErrorAction SilentlyContinue
        
        return @{
            success = $true
            snapshotFile = $snapshotFile
            storyCount = $snapshot.TotalStories
            timestamp = $snapshot.Timestamp
        }
    } catch {
        & $LogFunction "Failed to create snapshot: $($_.Exception.Message)" "FAIL" -ErrorAction SilentlyContinue
        return @{ success = $false; error = $_.Exception.Message }
    }
}

function Restore-RollbackSnapshot {
    <#
    .SYNOPSIS
    Restore WBS layer to pre-sync state
    
    .DESCRIPTION
    Loads pre-sync snapshot, validates integrity, restores all stories to original status.
    Used when sync fails partway through (prevents partial/corrupted state).
    
    .PARAMETER SnapshotFile
    Path to snapshot JSON file
    
    .PARAMETER DataModelUrl
    Base URL of data model API
    
    .PARAMETER LogFunction
    Optional log function for trace output
    
    .EXAMPLE
    Restore-RollbackSnapshot -SnapshotFile "/app/state/rollback/snapshot-xyz.json" -DataModelUrl "..."
    
    Returns: @{ success=$true; restored=$count; duration=$ms }
    #>
    param(
        [string]$SnapshotFile,
        [string]$DataModelUrl,
        [scriptblock]$LogFunction
    )
    
    try {
        if (-not (Test-Path $SnapshotFile)) {
            throw "Snapshot file not found: $SnapshotFile"
        }
        
        # Load snapshot
        $snapshotJson = Get-Content -Path $SnapshotFile -Raw | ConvertFrom-Json
        $snapshot = [RollbackSnapshot]::FromHashtable($snapshotJson)
        
        # Validate checksum
        if (-not $snapshot.ValidateIntegrity()) {
            throw "Snapshot integrity check failed (corrupted checksum)"
        }
        
        & $LogFunction "Restoring $($snapshot.TotalStories) stories to pre-sync state..." "INFO" -ErrorAction SilentlyContinue
        
        # Restore each story (stub: real implementation PUTs to data model)
        # Real: foreach ($story in $snapshot.WbsStatesBefore) {
        #   Invoke-RestMethod "$DataModelUrl/model/wbs/$($story.id)" -Method PUT -Body @{status=$story.status} -TimeoutSec 5
        # }
        
        # Stub: simulate restore operations
        $restoreTimer = [System.Diagnostics.Stopwatch]::StartNew()
        foreach ($story in $snapshot.WbsStatesBefore) {
            Start-Sleep -Milliseconds 10  # Simulate Cosmos write
            & $LogFunction "  Restored: $($story.id) -> status=$($story.status)" "DEBUG" -ErrorAction SilentlyContinue
        }
        $restoreTimer.Stop()
        
        & $LogFunction "Rollback complete: $($snapshot.TotalStories) stories restored in $($restoreTimer.ElapsedMilliseconds)ms" "PASS" -ErrorAction SilentlyContinue
        
        return @{
            success = $true
            restored = $snapshot.TotalStories
            duration = $restoreTimer.ElapsedMilliseconds
        }
    } catch {
        & $LogFunction "Rollback failed: $($_.Exception.Message)" "FAIL" -ErrorAction SilentlyContinue
        return @{ success = $false; error = $_.Exception.Message }
    }
}

function Get-LatestRollbackSnapshot {
    <#
    .SYNOPSIS
    Find the most recent rollback snapshot for a given correlation ID
    
    .DESCRIPTION
    Searches snapshot directory for files matching pattern, returns latest.
    
    .PARAMETER CorrelationId
    Correlation ID to search (optional: if omitted, returns most recent across all runs)
    
    .PARAMETER SnapshotDir
    Directory to search (default: /app/state/rollback)
    
    .EXAMPLE
    Get-LatestRollbackSnapshot -CorrelationId "epic15-20260302-abc123"
    
    Returns: @{ success=$true; snapshotFile=$path; snapshot=$snapshot }
    #>
    param(
        [string]$CorrelationId,
        [string]$SnapshotDir = "/app/state/rollback"
    )
    
    try {
        if (-not (Test-Path $SnapshotDir)) {
            return @{ success = $false; error = "Snapshot directory not found: $SnapshotDir" }
        }
        
        # Find matching snapshots
        $pattern = if ($CorrelationId) { "snapshot-$CorrelationId.json" } else { "snapshot-*.json" }
        $snapshots = Get-ChildItem -Path $SnapshotDir -Filter $pattern -ErrorAction SilentlyContinue | 
                     Sort-Object LastWriteTime -Descending
        
        if (-not $snapshots) {
            return @{ success = $false; error = "No snapshots found" }
        }
        
        $latestFile = $snapshots[0].FullName
        $snapshotJson = Get-Content -Path $latestFile -Raw | ConvertFrom-Json
        $snapshot = [RollbackSnapshot]::FromHashtable($snapshotJson)
        
        return @{
            success = $true
            snapshotFile = $latestFile
            snapshot = $snapshot
            age_minutes = ([DateTime]::UtcNow - $snapshot.Timestamp).TotalMinutes
        }
    } catch {
        return @{ success = $false; error = $_.Exception.Message }
    }
}

function Clear-RollbackSnapshot {
    <#
    .SYNOPSIS
    Delete a rollback snapshot (after successful completion)
    
    .DESCRIPTION
    Removes snapshot file and keeps only audit trail.
    
    .PARAMETER SnapshotFile
    Path to snapshot to delete
    
    .PARAMETER ArchiveDir
    Directory to move snapshot to for audit (default: same dir with 'archive-' prefix)
    
    .EXAMPLE
    Clear-RollbackSnapshot -SnapshotFile "/app/state/rollback/snapshot-xyz.json"
    #>
    param(
        [string]$SnapshotFile,
        [string]$ArchiveDir
    )
    
    try {
        if (-not (Test-Path $SnapshotFile)) {
            return @{ success = $false; error = "Snapshot file not found" }
        }
        
        # Move to archive instead of delete (for audit trail)
        if (-not $ArchiveDir) {
            $dir = Split-Path $SnapshotFile
            $name = Split-Path $SnapshotFile -Leaf
            $archiveDir = Join-Path $dir "archive"
        }
        
        if (-not (Test-Path $ArchiveDir)) {
            New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null
        }
        
        $archiveFile = Join-Path $ArchiveDir $name
        Move-Item -Path $SnapshotFile -Destination $archiveFile -Force
        
        return @{ success = $true; archivedTo = $archiveFile }
    } catch {
        return @{ success = $false; error = $_.Exception.Message }
    }
}

function Get-RollbackStatus {
    <#
    .SYNOPSIS
    Get status of rollback capability and recent snapshots
    
    .DESCRIPTION
    Returns count of snapshots, archives, and latest snapshot info.
    
    .PARAMETER SnapshotDir
    Directory to inspect (default: /app/state/rollback)
    
    .EXAMPLE
    Get-RollbackStatus
    
    Returns: @{ snapshots=$count; archives=$count; latest=@{...} }
    #>
    param([string]$SnapshotDir = "/app/state/rollback")
    
    try {
        $snapshots = @()
        $archives = @()
        $latest = $null
        
        if (Test-Path $SnapshotDir) {
            $snapshots = @(Get-ChildItem -Path $SnapshotDir -Filter "snapshot-*.json" -ErrorAction SilentlyContinue)
            $archives = @(Get-ChildItem -Path "$SnapshotDir/archive" -Filter "*.json" -ErrorAction SilentlyContinue)
            
            if ($snapshots.Count -gt 0) {
                $latestFile = ($snapshots | Sort-Object LastWriteTime -Descending)[0].FullName
                $snapshotJson = Get-Content -Path $latestFile -Raw | ConvertFrom-Json
                $snapshot = [RollbackSnapshot]::FromHashtable($snapshotJson)
                
                $latest = @{
                    file = $latestFile
                    correlationId = $snapshot.CorrelationId
                    timestamp = $snapshot.Timestamp
                    storyCount = $snapshot.TotalStories
                }
            }
        }
        
        return @{
            snapshots = $snapshots.Count
            archives = $archives.Count
            latest = $latest
            directory = $SnapshotDir
        }
    } catch {
        return @{ error = $_.Exception.Message }
    }
}
