import React, { Component } from 'react';
import MapPreview3D from './MapPreview3D';
import { Link } from 'react-router-dom';

class MapResult extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    // let stlId = null;
    let stlId = this.props.stlId;
    return (
      <div className="container">
        <nav className="nav-inline">
          <ul>
            <li><Link to="/design">Back to map design</Link></li>
            <li><Link to="/">Back to location search</Link></li>
          </ul>
        </nav>
        <div className="header">
          <h2 className="header-title">3D Map Preview</h2>
          
          {stlId ? (
            <div>
              <p>Rotate the map preview using the arrow keys or by using the buttons below the map.</p>
              <MapPreview3D mapStlUrl={"/api/map/stl/" + stlId} />
            </div>
          ) : (
            <div>
              <p>Map is loading, please wait...</p>
              <div className="spinner" style={{'width': '680px', 'height': '500px', 'border': '1px solid black'}}/>
            </div>
          )}
        </div>
      </div>
    );
  }
}

export default MapResult;