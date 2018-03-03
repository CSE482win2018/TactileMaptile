import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import LocationForm from './LocationForm';
import LinkButton from './LinkButton';
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

    this.setSearchResults = this.setSearchResults.bind(this);
  }

  render() {
    let classNames = this.props.highContrast ? this.contentClassNames.highContrast : this.contentClassNames.normal;
    return (
      <div className={classNames.containerDiv}>
        <nav className="nav-inline">
          <ul>
            {!this.props.highContrast ? (
              <li><LinkButton onClick={() => this.props.setHighContrast(true)}>View page in high contrast</LinkButton></li>
            ) : (
              <li><LinkButton onClick={() => this.props.setHighContrast(false)}>View page without high contrast</LinkButton></li>
            )}
          </ul>
        </nav>
        <div className="App-info">
          Design your own tactile maps to explore and navigate.
        </div>
        <div className="form-area">
          <LocationForm
            highContrast={this.props.highContrast}
            data={this.props.data}
            updateData={this.props.updateData}
            setSearchResults={this.setSearchResults}
            setMapAddress={this.props.setMapAddress}
            googleMapURL={config.googleMapsApiUri}
            loadingElement={<div/>} />
        </div>
      </div>
    );
  }

  setSearchResults(results) {
    this.props.updateData({searchResults: results});
    this.props.history.push('/searchresults');
  }
}

export default Home;
