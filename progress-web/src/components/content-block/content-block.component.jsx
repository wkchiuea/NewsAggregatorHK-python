import {useEffect, useState} from "react";
import {readFile} from "../../utils/fileReaderUtils";
import ContentElement from "../content-element/content-element.component";


const ContentBlock = ({dirPath, filePath}) => {

  const [fileContentList, setFileContentList] = useState([]);
  useEffect(() => {
    readFile(`${dirPath}/${filePath}`)
      .then(contentList => {
        setFileContentList(contentList);
      })
      .catch(e => {
        setFileContentList([]);
      });
  }, [dirPath, filePath]);

  return (
    <div>
      {
        fileContentList.map((content, index) => <ContentElement key={index} dirPath={dirPath} index={index} content={content} />)
      }
    </div>
  );
}

export default ContentBlock;