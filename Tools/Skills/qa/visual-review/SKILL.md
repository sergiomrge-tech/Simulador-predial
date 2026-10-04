---
name: visual-review
description: >
  Revisão visual com capturas reais (Blender ou Unity), review sheets e regressão por diferença de imagem
  com Pillow. Use antes de qualquer gate visual ou quando uma mudança puder alterar a aparência do mundo.
---

# Revisão visual — capturas reais, nunca mockups

## Regras
- Só vale captura renderizada de arquivo salvo e reaberto em processo novo (`verify_world_v1_5.py`).
- Olhe cada imagem antes de declarar aprovação. Registre o que está ruim, sem só listar o que funciona.
- Low-poly ou blockout nunca é apresentado como arte final; marque o estágio na própria folha.
- VEIN serve de régua de qualidade (densidade, materialidade, luz), não de fonte.

## Câmeras
- As câmeras ficam salvas no `.blend` (`CAM_*`) e funcionam como bookmarks reprodutíveis. Novas vistas entram no gerador, não à mão.
- Cada distrito tem uma vista de cima ortográfica inclinada e uma vista baixa (escala humana) quando houver arte.

## Review sheet
- Gerada por script a partir dos relatórios JSON (validação, rotas, reaberturas), para que os números nunca sejam digitados à mão.
- Comparação lado a lado com o marco anterior (`Reviews/W1` × `Reviews/W1_5`).

## Regressão por diferença de imagem (sem dependências novas)
```python
from PIL import Image, ImageChops, ImageStat
a = Image.open("antes.jpg").convert("RGB"); b = Image.open("depois.jpg").convert("RGB")
diff = ImageChops.difference(a, b)
score = sum(ImageStat.Stat(diff).mean) / 3        # 0 = idêntico
bbox = diff.getbbox()                              # região alterada
```
- JPEG tem ruído: use limiar (> 2.0 de média) e compare só com a mesma resolução e câmera.
- Para a Unity, o equivalente é a captura em PlayMode (Unity Test Framework + `ScreenCapture`) com a mesma métrica.
