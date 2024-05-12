import {getFilePaths} from "../../utils/fileReaderUtils";
import ContentBlock from "../content-block/content-block.component";
import {useContext} from "react";
import {FileMapContext} from "../../contexts/fileMap.context";


const ContentPage = ({targetPath}) => {
  const {fileMap} = useContext(FileMapContext);
  const [dirPath, filePath] = getFilePaths(fileMap, targetPath);

  return (
    <div>
      <ContentBlock dirPath={dirPath} filePath={filePath} />
    </div>
  );
}

export default ContentPage;