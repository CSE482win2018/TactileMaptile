import React from 'react';

let PlaceResult = (props) => {
  let {address, ...rest} = props;
  return (
    <span {...rest}>
      {address.hasOwnProperty('name') && <strong>{address.name}</strong>}
      {address.hasOwnProperty('name') && <br/>}
      {address.formatted_address}
    </span>
  );
}

export default PlaceResult;
