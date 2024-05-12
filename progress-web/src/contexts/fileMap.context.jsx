import React, {createContext, useEffect, useState} from "react";

export const FileMapContext = createContext();

export const FileMapProvider = ({children}) => {
  const [fileMap, setFileMap] = useState(null);

  useEffect(() => {
    const fetchFileMap = async () => {
      try {
        const res = await fetch(`${process.env.PUBLIC_URL}/resources/fileMap.json`);
        if (!res.ok) {
          throw new Error("Network response is not ok");
        }
        const data = await res.json();
        setFileMap(data);
      } catch (error) {
        console.error("Error fetching text file:", error);
      }
    }

    fetchFileMap();
  }, []);

  return (
    <FileMapContext.Provider value={{fileMap}}>
      {children}
    </FileMapContext.Provider>
  );

}
