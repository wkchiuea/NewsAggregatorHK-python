import './App.css';
import Banner from "./components/banner/banner.component";
import ContentPage from "./components/content-page/content-page";
import {useState} from "react";
import {getProgressList} from "./utils/fileReaderUtils";


const App = () => {

  const progressList = getProgressList();
  const [activeContent, setActiveContent] = useState("introduction");

  const updateContentHandler = (key) => {
    setActiveContent(key);
  }

  return (
    <div className="container-fluid">
      <Banner imageUrl={`${process.env.PUBLIC_URL}/resources/banner.jpg`} />

      <div className="container">
        <div className="row">
          <div className="col-3">
            <div className="d-flex flex-column">
              <button className="btn btn-outline-success mb-2" onClick={() => updateContentHandler("introduction")}>Introduction</button>
              <button className="btn btn-outline-success mb-2" onClick={() => updateContentHandler("methodology")}>Methodology</button>
              {
                progressList.map((pDate, index) => {
                  return <button key={index} onClick={() => updateContentHandler(pDate)} className="btn btn-outline-secondary mb-2">~ {pDate}</button>;
                })
              }
            </div>
          </div>
          <div className="col-9">
            <ContentPage target={activeContent} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
