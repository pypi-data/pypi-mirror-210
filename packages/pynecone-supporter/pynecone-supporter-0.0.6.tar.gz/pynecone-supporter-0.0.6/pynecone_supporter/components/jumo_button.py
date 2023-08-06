import pynecone as pc

#https://www.npmjs.com/package/react-supporter
class JumoButton(pc.Component):
    library = "react-supporter" #from 뒤 npm 패키지 이름
    tag = "JumoButton" #import 뒤 리액트 컴포넌트의 태그 이름
    
    #리액트 속성에 대응
    background_color: pc.Var[str]
    font_color: pc.Var[str]

    #리액트 이벤트에 대응
    @classmethod
    def get_controlled_triggers(cls):
        return {"on_click": pc.EVENT_ARG} #onClick

jumo_button = JumoButton.create
