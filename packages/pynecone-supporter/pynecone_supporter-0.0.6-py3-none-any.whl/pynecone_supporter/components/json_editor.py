import pynecone as pc

#https://www.npmjs.com/package/react-jsondata-editor
class JsonEditor(pc.Component):
    library = "react-jsondata-editor" #from 뒤 npm 패키지 이름
    tag = "JsonEditor" #import 뒤 리액트 컴포넌트의 태그 이름
    
    #리액트 속성에 대응
    json_object: pc.Var[str] 

    #리액트 이벤트에 대응
    @classmethod
    def get_controlled_triggers(cls):
        return {"on_change": pc.EVENT_ARG} #onChange

json_editor = JsonEditor.create
