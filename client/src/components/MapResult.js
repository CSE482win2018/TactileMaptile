import React, { Component } from 'react';
import MapPreview3D from './MapPreview3D';
import { Link } from 'react-router-dom';

class MapResult extends Component {
  constructor(props) {
    super(props);
  }

  render() {
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
          {this.props.stlId ? (
            <MapPreview3D mapStlUrl={"/api/map/stl/" + this.props.stlId} />
          ) : (
            <div>LOADING</div>
          )}
        </div>
      </div>
    );
  }
}

export default MapResult;