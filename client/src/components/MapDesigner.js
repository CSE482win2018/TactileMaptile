import React, { Component } from "react";
import { withRouter, Link } from "react-router-dom";
import MapPreviewOl from './MapPreviewOl';
import '../App.css';
import '../turret.css';

class MapDesigner extends Component {
  constructor(props) {
    super(props);
    this.state = {
      showPreview: false,
      stlId: null,
    };

    this.handleDesignSubmit = this.handleDesignSubmit.bind(this);
  }

  render() {
    console.log(this.props);
    let address = this.props.data.address;
    return (
      <div style={{display: 'flex'}} className="container">
        <div style={{margin: '10px'}}>
          <nav className="nav-inline">
            <ul>
              <li><Link to="/">Back to location search</Link></li>
            </ul>
          </nav>
          <div className="header">
            <h2 className="header-title">Map designer</h2>
          </div>
          <div>
          <p>Using address: {address.formatted_address}</p>
          <form onSubmit={this.handleDesignSubmit}>
            <fieldset>
              <legend>Map options</legend>
              <label htmlFor="size-select">Map print size</label>
              <select name="size-select" onChange={(event) => this.props.updateData({size: +event.target.value})} defaultValue={17}>
                <option value="13">13 cm / 5.1 inches across </option>
                <option value="17">17 cm / 6.7 inches across (good for personal use)</option>
                <option value="20">20 cm / 7.9 inches across</option>
              </select>
              <label htmlFor="size-select">Map scale</label>
              <select name="scale-select" onChange={(event) => this.props.updateData({scale: +event.target.value})} defaultValue={2400}>
                <option value="1000">1:1000 – single buildings or points of interest</option>
                <option value="1400">1:1400</option>
                <option value="1800">1:1800 – dense cities</option>
                <option value="2400">1:2400 – default</option>
                <option value="3200">1:3200 – average suburbs</option>
                <option value="4200">1:4200</option>
                <option value="5600">1:5600 – very sparsely built areas</option>
                <option value="7500">1:7500</option>
                <option value="9999">1:9999 – areas with only large roads</option>
              </select>
              <button type="submit" className="button color-white background-secondary">Create map</button>
            </fieldset>
          </form>
          </div>
        </div>
        <div style={{display: 'flex', alignItems: 'center', margin: '10px'}}>
          <MapPreviewOl maxSize={350} data={this.props.data} address={address} updateData={this.props.updateData}/>
        </div>
      </div>
    );
  }

  handleDesignSubmit(event) {
    event.preventDefault();
    
    let data = {
      min_lat: this.props.data.minLat,
      max_lat: this.props.data.maxLat,
      min_lng: this.props.data.minLng,
      max_lng: this.props.data.maxLng,
      scale: this.props.data.scale,
      size: this.props.data.size
    };
    let formData = new URLSearchParams();
    Object.keys(data).forEach(key => {
      formData.append(key, data[key]);
    });
    console.log(formData);
    fetch('/api/map', {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: formData.toString(), // must match 'Content-Type' header
      method: 'POST', // *GET, PUT, DELETE, etc.
    })
    .then(response => response.json())
    .then(json => {
      console.log(json)
      this.props.setStlId(json.id);
    });

    this.props.navigateToMapResult();
  }
}

export default withRouter(MapDesigner);