import pynecone as pc

#https://www.npmjs.com/package/react-webcam
class Webcam(pc.Component):
    library = "react-webcam" #from 뒤 npm 패키지 이름
    tag = "Webcam" #import 뒤 리액트 컴포넌트의 태그 이름

webcam = Webcam.create
