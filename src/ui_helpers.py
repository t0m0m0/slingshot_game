import pygame

# ヘルパー関数: 角丸の長方形を描画
def draw_rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
    """
    角丸の長方形を描画する
    surface: 描画対象のサーフェス
    color: 塗りつぶしの色
    rect: 長方形の位置とサイズ (x, y, width, height)
    radius: 角の丸みの半径
    border: 枠線の太さ (0なら枠線なし)
    border_color: 枠線の色 (Noneなら枠線なし)
    """
    rect = pygame.Rect(rect)
    
    # 角の丸みが長方形の半分を超えないようにする
    radius = min(radius, rect.width // 2, rect.height // 2)
    
    if border > 0 and border_color:
        # 枠線用の大きい長方形を描画
        outer_rect = rect.copy()
        pygame.draw.rect(surface, border_color, outer_rect, border_radius=radius)
        
        # 内側の塗りつぶし用の小さい長方形を描画
        inner_rect = rect.inflate(-border*2, -border*2)
        pygame.draw.rect(surface, color, inner_rect, border_radius=radius)
    else:
        # 枠線なしの場合は単純に塗りつぶし
        pygame.draw.rect(surface, color, rect, border_radius=radius)

# ヘルパー関数: モダンなボタンを描画
def draw_button(surface, text, rect, font, colors, is_selected=False, is_hovered=False):
    """
    モダンなボタンを描画する
    surface: 描画対象のサーフェス
    text: ボタンのテキスト
    rect: ボタンの位置とサイズ (x, y, width, height)
    font: テキストのフォント
    colors: 色の辞書 (BLACK, LIGHT_BLUE, LIGHT_GREEN)
    is_selected: 選択されているかどうか
    is_hovered: マウスが乗っているかどうか
    """
    # ボタンの色を決定
    if is_selected:
        bg_color = colors["LIGHT_GREEN"]
        border_color = (0, 100, 0)
    elif is_hovered:
        bg_color = (200, 230, 255)
        border_color = (70, 130, 180)
    else:
        bg_color = colors["LIGHT_BLUE"]
        border_color = (70, 130, 180)
    
    # 角丸の長方形を描画
    draw_rounded_rect(surface, bg_color, rect, radius=10, border=2, border_color=border_color)
    
    # テキストを描画
    text_surf = font.render(text, True, colors["BLACK"])
    text_rect = text_surf.get_rect(center=(rect[0] + rect[2]//2, rect[1] + rect[3]//2))
    surface.blit(text_surf, text_rect)
    
    return rect  # ボタンの領域を返す
