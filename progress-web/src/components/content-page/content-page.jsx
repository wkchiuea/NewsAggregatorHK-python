import {getFileMapConfig} from "../../utils/fileReaderUtils";
import ContentBlock from "../content-block/content-block.component";


const ContentPage = ({target}) => {

  const [basePath, section, fileList] = getFileMapConfig(target);

  return (
    <div>
      {
        fileList.map((filePath, index) =>
          <ContentBlock dirPath={`${basePath}/${section}`} filePath={filePath} key={index} />
        )
      }
    </div>
  );
}

export default ContentPage;