# Validação da interface r0.2 — 30/10/2026

**Resultado: pacote de cotação gerado e verificado.** PCB de 15 × 20 mm, 1,6 mm, duas camadas, 17 SMD no topo e 19 pontos para fios. Projeto editável em formato KiCad 10.

| Conferência | Resultado |
|---|---|
| ERC KiCad 10.0.7 | 0 violações |
| DRC KiCad 10.0.7, incluindo zonas preenchidas | 0 violações |
| Conexões abertas no DRC | 0 |
| Paridade PCB / esquemático | 0 divergências |
| Tabela elétrica / esquema exportado / PCB | 65 pares de pino e rede conferidos |
| Continuidade independente, duas camadas | 0 redes abertas |
| Separação mínima de cobre entre redes, sem zonas | aproximadamente 0,18 mm; mínimo de projeto 0,153 mm |
| Sobreposição dos envelopes de componentes | 0 |
| Contorno e apoios contra CAD | 15 × 20 mm; centros dos quatro furos coincidentes |
| Menor folga nominal do canto da PCB à parede | 1,38 mm |
| Leitura independente de Gerber/Excellon | 8 camadas gráficas, 29 furos metalizados e 4 não metalizados |
| Montagem | 17 posições no topo, correspondentes à BOM |

O roteamento inicial tem nove vias; a revisão final acrescenta uma via GND fora dos pads de pasta para conectar a área inferior de referência. São dez vias de 0,3 mm e dezenove furos metalizados de 0,5 mm. Há quatro furos de montagem de 2,2 mm, não metalizados.

Foram inspecionados o esquemático exportado e os desenhos derivados dos Gerbers de cobre e serigrafia. O leitor independente registra avisos informativos sobre G90 no cabeçalho Excellon exportado pelo KiCad e ausência de pasta inferior; a placa tem montagem somente superior. Nenhum desses avisos impedeu a leitura, e as contagens de furos foram conferidas. Os SVGs coloridos do Gerbonara usam filtros de navegador; as imagens por camada são a referência raster para inspeção.

O encaixe é **nominal no CAD**, sem medição da peça impressa ou representação completa das curvas de fios. Imprimir o molde a 100% e verificar o conjunto real. Usar cabeças de parafuso até Ø3,5 mm e conferir a fixação nos pilares.

O projeto ainda não foi fabricado ou ensaiado. A integridade do clock dividido em três ramos, os níveis na entrada das fitas, o firmware SPI quad, o buck, a temperatura e a integração com bateria/Hall permanecem sujeitos a ensaio. Chave, fusível, potência dos LEDs e capacitor de 1000 µF são externos. Este pacote não encerra as pendências mecânicas do rotor.
