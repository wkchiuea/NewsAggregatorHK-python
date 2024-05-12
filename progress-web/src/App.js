import './App.css';
import Banner from "./components/banner/banner.component";
import ContentPage from "./components/content-page/content-page";
import {useContext, useLayoutEffect, useState} from "react";
import {FileMapContext} from "./contexts/fileMap.context";


const App = () => {

  const {fileMap} = useContext(FileMapContext);
  const [progressList, setProgressList] = useState([]);
  const [activeContent, setActiveContent] = useState(null);

  useLayoutEffect(() => {
    if (fileMap && fileMap['progress']) {
      const progress = fileMap['progress'];
      setProgressList(progress);

      if (progress.length > 0) {
        setActiveContent(progress[0]);
      }
    }
  }, [fileMap]);

  const updateContentHandler = (key) => {
    setActiveContent(key);
  }

  if (!activeContent) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container-fluid">
      <Banner imageUrl={`${process.env.PUBLIC_URL}/resources/banner.jpg`} />

      <div className="container">
        <div className="row">
          <div className="col-3">
            <div className="d-flex flex-column">
              {
                progressList.map((pDate, index) => {
                  return <button key={index} onClick={() => updateContentHandler(pDate)} className="btn btn-outline-secondary mb-2">~ {pDate}</button>;
                })
              }
            </div>
          </div>
          <div className="col-9">
            <ContentPage targetPath={activeContent} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
