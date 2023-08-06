import pynecone as pc

#https://www.npmjs.com/package/react-colorful
class ColorPicker(pc.Component):
    library = "react-colorful" #from 뒤 npm 패키지 이름
    tag = "HexColorPicker" #import 뒤 리액트 컴포넌트의 태그 이름
    
    #리액트 속성에 대응
    color: pc.Var[str] #color

    #리액트 이벤트에 대응
    @classmethod
    def get_controlled_triggers(cls):
        return {"on_change": pc.EVENT_ARG} #onChange

color_picker = ColorPicker.create
