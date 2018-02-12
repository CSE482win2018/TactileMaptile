import React, { Component } from "react";
import { withRouter, Link } from "react-router-dom";
import MapPreview from './components/MapPreview';

class MapDesigner extends Component {
  constructor(props) {
    super(props);
    this.state = {
      options: {
        width: null,
        height: null
      },
      showPreview: false
    };

    this.handleDesignSubmit = this.handleDesignSubmit.bind(this);
  }

  render() {
    let address = this.props.address;
    if (!address) {
      address = {
        formatted_address: "123 foo st"
      };
    }
    return (
      <div className="container">
        <nav className="nav-inline">
          <ul>
            <li><Link to="/">Back to location search</Link></li>
          </ul>
        </nav>
        <div className="header">
        <h2 className="header-title">Map designer</h2>
        </div>
        <p>Using address: {address.formatted_address}</p>
        <form onSubmit={this.handleDesignSubmit}>
          <fieldset>
            <legend>Map options</legend>
            <div className="field">
              <label htmlFor="map-width">Map size, east to west (kilometers)</label>
              <input id="map-width" type="number" min="1" max="5" placeholder="1" onChange={event => this.setState({options: {...this.state.options, width: +event.target.value}})} />
            </div>
            <div className="field">
              <label htmlFor="map-height">Map size, north to south (kilometers)</label>
              <input id="map-height" type="number" min="1" max="5" placeholder="1" onChange={event => this.setState({options: {...this.state.options, height: +event.target.value}})} />
            </div>
            <button type="submit" className="button color-white background-secondary">Create map</button>
          </fieldset>
        </form>
        {this.state.showPreview && (
          <MapPreview mapStlUrl="/api/map/stl" />
        )}
      </div>
    );
  }

  handleDesignSubmit(event) {
    event.preventDefault();
    this.setState({
      showPreview: true
    });
  }
}

export default withRouter(MapDesigner);