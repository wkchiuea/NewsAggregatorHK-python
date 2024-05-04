import fileMap from "../fileMap.json";


export const getProgressList = () => {
  return fileMap["progress"];
}

export const getFileMapConfig = key => {
  return [fileMap["basePath"], key, fileMap[key]];
};

export const readFile = filepath => {
  return fetch(filepath).then(res => {
    if (!res.ok) {
      throw new Error("Network response is not ok");
    }
    return res.text();
  }).then(text => {
    const contentList = text.split("\n");
    return contentList;
  }).catch(error => {
    console.error("Error fetching text file:", error);
  });

};