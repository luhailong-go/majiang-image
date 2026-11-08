$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$fontCollection=[System.Drawing.Text.PrivateFontCollection]::new()
$fontCollection.AddFontFile('C:\Windows\Fonts\simkai.ttf')
$fontFamily=$fontCollection.Families[0]
$glyphs=[ordered]@{}
$invariant=[System.Globalization.CultureInfo]::InvariantCulture
function F([single]$n){return $n.ToString('0.###',$invariant)}
foreach($ch in @('梅','兰','竹','菊','春','夏','秋','冬')){
 $path=[System.Drawing.Drawing2D.GraphicsPath]::new()
 $path.AddString($ch,$fontFamily,0,256,[System.Drawing.PointF]::new(0,0),[System.Drawing.StringFormat]::GenericTypographic)
 $b=$path.GetBounds();$pts=$path.PathPoints;$types=$path.PathTypes;$parts=[System.Collections.Generic.List[string]]::new()
 for($i=0;$i -lt $pts.Length;$i++){
  $kind=$types[$i] -band 7
  if($kind -eq 0){$parts.Add('M '+(F $pts[$i].X)+' '+(F $pts[$i].Y))}
  elseif($kind -eq 1){$parts.Add('L '+(F $pts[$i].X)+' '+(F $pts[$i].Y))}
  elseif($kind -eq 3){$parts.Add('C '+(F $pts[$i].X)+' '+(F $pts[$i].Y)+' '+(F $pts[$i+1].X)+' '+(F $pts[$i+1].Y)+' '+(F $pts[$i+2].X)+' '+(F $pts[$i+2].Y));$i+=2}
  if(($types[$i] -band 128) -ne 0){$parts.Add('Z')}
 }
 $glyphs[$ch]=[ordered]@{path=($parts -join ' ');bounds=@($b.X,$b.Y,$b.Width,$b.Height)};$path.Dispose()
}
[ordered]@{font='KaiTi / simkai.ttf';method='GDI+ glyph outlines; font file not redistributed';glyphs=$glyphs} | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath 'work/full-game-props/flower-glyphs.json' -Encoding utf8
$fontCollection.Dispose()
Write-Output '8 flower glyph outlines exported'
