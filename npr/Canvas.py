from skimage import io,transform
import numpy as np

class Canvas:
    def __init__(self):
        self.canvas=None
        self.paper=None
        self.width=None
        self.height=None
        self.palette=[]

    def set_canvas(self,width,height):
        self.width=width
        self.height=height

    def set_paper(self,paper):
        img=io.imread(paper)
        img=transform.resize(img, (self.height,self.width))
        self.canvas=np.ndarray(shape=(self.height,self.width,4))
        for i in range(self.height):
		for j in range(self.width):
			self.canvas[i][j][0:3]=img[i][j]
			self.canvas[i][j][3]=1.0
        #io.imshow(self.canvas)
        #io.show()

    def set_palettecolor(self,color):
        c=[color]
        self.palette.extend(c)

if __name__=='__main__':
    canvas=Canvas()
    canvas.set_canvas(600,400)
    canvas.set_paper('paper.jpg')
