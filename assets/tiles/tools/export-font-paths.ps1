$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$assetRoot = Split-Path -Parent $PSScriptRoot
$fontCollection = [System.Drawing.Text.PrivateFontCollection]::new()
$fontCollection.AddFontFile('C:\Windows\Fonts\simkai.ttf')
$fontFamily = $fontCollection.Families[0]
$glyphs = [ordered]@{}
$chars = @('一','二','三','四','五','六','七','八','九','萬','东','南','西','北','中','發')
$invariant = [System.Globalization.CultureInfo]::InvariantCulture
function Format-PathNumber([single]$n) { return $n.ToString('0.###', $invariant) }
foreach ($ch in $chars) {
    $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $path.AddString($ch, $fontFamily, 0, 256, [System.Drawing.PointF]::new(0,0), [System.Drawing.StringFormat]::GenericTypographic)
    $bounds = $path.GetBounds()
    $points = $path.PathPoints
    $types = $path.PathTypes
    $parts = [System.Collections.Generic.List[string]]::new()
    for ($i=0; $i -lt $points.Length; $i++) {
        $kind = $types[$i] -band 7
        if ($kind -eq 0) {
            $parts.Add('M ' + (Format-PathNumber $points[$i].X) + ' ' + (Format-PathNumber $points[$i].Y))
        } elseif ($kind -eq 1) {
            $parts.Add('L ' + (Format-PathNumber $points[$i].X) + ' ' + (Format-PathNumber $points[$i].Y))
        } elseif ($kind -eq 3) {
            $parts.Add('C ' + (Format-PathNumber $points[$i].X) + ' ' + (Format-PathNumber $points[$i].Y) + ' ' + (Format-PathNumber $points[$i+1].X) + ' ' + (Format-PathNumber $points[$i+1].Y) + ' ' + (Format-PathNumber $points[$i+2].X) + ' ' + (Format-PathNumber $points[$i+2].Y))
            $i += 2
        }
        if (($types[$i] -band 128) -ne 0) { $parts.Add('Z') }
    }
    $glyphs[$ch] = [ordered]@{path=($parts -join ' ');bounds=@($bounds.X,$bounds.Y,$bounds.Width,$bounds.Height)}
    $path.Dispose()
}
[ordered]@{font='KaiTi / simkai.ttf';method='GDI+ GraphicsPath glyph outlines; font file is not redistributed';glyphs=$glyphs} | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath (Join-Path $assetRoot 'source\glyph-outlines.json') -Encoding utf8
$fontCollection.Dispose()
Write-Output ('Exported '+$glyphs.Count+' outlined glyphs')
