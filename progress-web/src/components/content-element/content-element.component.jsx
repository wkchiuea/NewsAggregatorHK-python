

const ContentElement = ({dirPath, index, content}) => {

  if (index === 0) {

    return <h4 key={index}>{content}</h4>;

  } else if (content.startsWith("<IMG>")) {
    const imgList = content.replace("<IMG>", "").split(",");

    return (
      <div className="row">
        {
          imgList.map((imgFile, index) =>
            <div className="col" key={index}>
              <img src={`${dirPath}/${imgFile}`} className="img-fluid" />
            </div>
          )
        }
      </div>
    );

  }

  return <p key={index}>{content}</p>;

}


export default ContentElement;