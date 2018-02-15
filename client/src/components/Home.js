import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import LocationForm from './LocationForm';
import * as config from '../config.json';
import '../App.css';
import '../turret.css';

class Home extends Component {
  constructor(props) {
    super(props);
    this.contentClassNames = {
      normal: {
        containerDiv: "container"
      },
      highContrast: {
        containerDiv: "container background-black color-white"
      }
    }
  }

  render() {
    let classNames = this.props.highContrast ? this.contentClassNames.highContrast : this.contentClassNames.normal;
    return (
      <div className={classNames.containerDiv}>
        <nav className="nav-inline">
          <ul>
            {!this.props.highContrast ? (
              <li><Link to="/?highContrast">View page in high contrast</Link></li>
            ) : (
              <li><Link to="/">View page without high contrast</Link></li>
            )}
          </ul>
        </nav>
        <div className="App-info">
          Design your own tactile maps to explore and navigate.
        </div>
        <div className="form-area">
          <LocationForm
            data={this.props.data}
            updateData={this.props.updateData}
            setMapAddress={this.props.setMapAddress}
            googleMapURL={config.googleMapsApiUri}
            loadingElement={<div/>} />
        </div>
      </div>
    );
  }
}

export default Home;