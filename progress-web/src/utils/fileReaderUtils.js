
export const getFilePaths = (fileMap, key) => {
  const dirPath = `${fileMap["basePath"]}/${key}`;
  const filePath = `${key}.txt`;
  return [dirPath, filePath];
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