

const Banner = ({imageUrl}) => {
  return (
    <div className="row mb-4">
      <img src={imageUrl} className="img-fluid" alt="banner"/>
    </div>
  );
}

export default Banner;