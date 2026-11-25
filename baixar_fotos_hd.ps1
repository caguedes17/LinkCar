# LinkCar: fotografias ilustrativas dos modelos (Wikimedia Commons).
# Execute UMA VEZ na raiz do LinkCar usando PowerShell (com internet).
# Requer os arquivos deste pacote copiados para o projeto.
$ErrorActionPreference = 'Stop'
$pasta = Join-Path $PSScriptRoot 'static\img\fotos'
New-Item -ItemType Directory -Force -Path $pasta | Out-Null
$arquivos = @(
    @{ Nome='honda-civic-2012.jpg'; Url='https://upload.wikimedia.org/wikipedia/commons/0/0d/2012_Honda_Civic_EX_sedan.jpg' }
    @{ Nome='fiat-strada-2015.jpg'; Url='https://upload.wikimedia.org/wikipedia/commons/5/50/Fiat_Strada_1.4_Trekking_Crew_Cab_2015_%2816887528745%29.jpg' }
    @{ Nome='honda-civic-2016.jpg'; Url='https://upload.wikimedia.org/wikipedia/commons/6/6f/Honda_Civic_2016.jpg' }
    @{ Nome='honda-civic-hatch-2016.jpg'; Url='https://commons.wikimedia.org/wiki/Special:Redirect/file/Honda_Civic_5d_-_prz%C3%B3d_%28MSP16%29.jpg' }
    @{ Nome='jeep-compass-2018.jpg'; Url='https://upload.wikimedia.org/wikipedia/commons/9/96/2018_Jeep_Compass_Latitude_2.4L_front_4.20.19.jpg' }
    @{ Nome='volkswagen-polo-2019.jpg'; Url='https://upload.wikimedia.org/wikipedia/commons/a/aa/Volkswagen_Polo_2019.jpg' }
    @{ Nome='ford-mustang-2018.jpg'; Url='https://upload.wikimedia.org/wikipedia/commons/5/5d/2018_Ford_Mustang_GT_5.0_Front.jpg' }
    @{ Nome='fiat-doblo-2017.jpg'; Url='https://upload.wikimedia.org/wikipedia/commons/3/35/2017_Fiat_Doblo_%28263_Series_II%29_SWB_van_%282018-09-03%29_01.jpg' }
)
foreach ($foto in $arquivos) {
    $destino = Join-Path $pasta $foto.Nome
    if ((Test-Path $destino) -and ((Get-Item $destino).Length -gt 90000)) { Write-Host "OK (existente): $($foto.Nome)"; continue }
    try {
        Invoke-WebRequest -Uri $foto.Url -OutFile $destino -MaximumRedirection 5 -TimeoutSec 90 -Headers @{ 'User-Agent'='Mozilla/5.0 (LinkCar - projeto academico)' }
        $tamanho = (Get-Item $destino).Length
        if ($tamanho -lt 90000) { throw "Arquivo incompleto: $tamanho bytes" }
        Write-Host "Baixada: $($foto.Nome) ($tamanho bytes)" -ForegroundColor Green
    } catch {
        Write-Warning "Nao foi possivel baixar $($foto.Nome): $($_.Exception.Message)"
        if (Test-Path $destino) { Remove-Item $destino -Force }
        Write-Host 'A interface tentara usar a foto online automaticamente.'
    }
}
Write-Host 'Concluido. Reinicie o Flask e pressione Ctrl+F5 no navegador.' -ForegroundColor Cyan
