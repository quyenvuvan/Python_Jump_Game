import pygame

def clip(surf,x,y,x_size,y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

def swap_color(img,old_c,new_c):
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img,(0,0))
    surf.set_colorkey((0,0,0))
    return surf

class Font:
    def __init__(self,path,color):
        self.spacing=2
        self.character_order=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.','-',',',':','+','\'','!','?','0','1','2','3','4','5','6','7','8','9','(',')','/','_','=','\\','[',']','*','"','<','>',';']
        font_img=pygame.image.load(path).convert()
        font_img.set_colorkey((0,0,0))
        font_img=swap_color(font_img,(255,0,0),color)
        currrent_char_width=0
        self.characters={}
        character_count=0
        for x in range(font_img.get_width()):
            c=font_img.get_at((x,0))
            if c[0]==127:
                char_img=clip(font_img,x-currrent_char_width,0,currrent_char_width,font_img.get_height())
                self.characters[self.character_order[character_count]]=char_img
                character_count+=1
                currrent_char_width=0
            else:
                currrent_char_width+=1
        self.space_width=self.characters['A'].get_width()

    def width(self, text):
        text_width = 0
        for char in text:
            if char == ' ':
                text_width += self.space_width+self.spacing
            else:
                text_width += self.characters[char].get_width()+self.spacing
        return text_width

    def render(self,surf,text,loc):
        x_offset=0
        for char in text:
            if char!=' ':
                surf.blit(self.characters[char],(loc[0]+x_offset,loc[1]))
                x_offset+=self.characters[char].get_width()+self.spacing
            else:
                x_offset+=self.space_width+self.spacing
