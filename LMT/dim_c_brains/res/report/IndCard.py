'''
Created on 3 juin 2025

@author: Fab
'''

class IndCard(object):
    


    def __init__(self, name, style="primary" ):
        
        #self.items = []
        self.html = ""
        self.name = name
        self.style= style
        
    def addProgress(self , val, fontColor="white", barColor="blue", backgroundColor="white", text="default text", sideText ="side:" ):
                
        self.html+= f"""
        <div style="display:inline-block;width:100%;">
        <div>
        <div style="width:20%;float:left;font-size: 0.75rem;padding-right:10px;text-align:right;">{sideText}</div>
        <div class="progress" style="background-color:{backgroundColor};">
        <div class="progress-bar" role="progressbar" style="width: {val}%;color:{fontColor};background-color:{barColor};" aria-valuenow="{val}" aria-valuemin="0" aria-valuemax="100">{text}</div>
        </div>
        </div>
        </div>
        """
    
    def addBadge(self , text, fontColor="white", backgroundColor = "rgb(13,110,253)"):
        self.html+=f"""<span class="badge" style="margin:4px;color:{fontColor};background-color:{backgroundColor}">{text}</span>"""
        
    def render(self):
        
        self.html = f"""
        <div class="col-xl-3 col-md-6">
        <div class="card bg-{self.style} text-white mb-4">
            <div class="card-body">{self.name}</div>
            <div class="card-footer align-items-center justify-content-between">
                {self.html}
                
                
                            
            </div>
        </div>
        </div>
        """

                        
                        
        
        return self.html
        
        

        