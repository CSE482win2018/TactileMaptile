import React, { Component } from 'react';
import { withRouter, Link } from "react-router-dom";
import MapPreviewOl from './MapPreviewOl';
import '../App.css';
import '../turret.css';

class MapDesigner extends Component {
  constructor(props) {
    super(props);
    this.state = {
      busRouteStates: this.getRouteStates(props.data.mapData.busStops || {})
    };

    this.handleDesignSubmit = this.handleDesignSubmit.bind(this);
    this.handleBusToggle = this.handleBusToggle.bind(this);
    this.handleAllBusesToggle = this.handleAllBusesToggle.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.data.mapData.busRoutes != nextProps.data.mapData.busRoutes) {
      this.setState({
        busRouteStates: this.getRouteStates(nextProps.data.busRoutes || {})
      });
    }
  }

  render() {
    let address = this.props.data.address;
    let mapData = this.props.data.mapData;
    return (
      <div className="row-container">
        <div className="container">
          <nav className="nav-inline">
            <ul>
              {!this.props.highContrast ? (
                <li><a role="button" tabindex="0" onClick={() => this.props.setHighContrast(true)}>View page in high contrast</a></li>
              ) : (
                <li><a role="button" tabindex="0" onClick={() => this.props.setHighContrast(false)}>View page without high contrast</a></li>
              )}
              <li><Link to="/">Back to home</Link></li>
              <li><Link to="/size">Back to set map size</Link></li>
            </ul>
          </nav>
          <div className="header">
            <h2 className="header-title">Map designer</h2>
          </div>
          <div>
          <p>Using address: {address.formatted_address}</p>
          <form onSubmit={this.handleDesignSubmit}>
            <fieldset>
              <legend>Navigation</legend>
              {this.getBusStopUI(mapData.busStops)}
              <button type="submit" className="button color-white background-secondary">Create map</button>
            </fieldset>
          </form>
          </div>
        </div>
        <div style={{display: 'flex', alignItems: 'center', margin: '10px'}}>
          <MapPreviewOl data={this.props.data} address={address} updateData={this.props.updateData}/>
        </div>
      </div>
    );
  }

  handleDesignSubmit(event) {
    event.preventDefault();
    this.props.updateData({
      mapCreated: false
    });

    let postData = {
      busStops: Object.keys(this.state.busRouteStates)
        .filter(key => this.state.busRouteStates[key])
    }
    
    fetch(`/api/map/${this.props.stlId}/create`, {
      headers: {
        'content-type': 'application/json'
      },
      body: JSON.stringify(postData), // must match 'Content-Type' header
      method: 'POST', // *GET, PUT, DELETE, etc.
    })
    .then(response => response.json())
    .then(json => {
      console.log(json)
      this.props.updateData({
        mapCreated: true
      });
    });

    this.props.history.push('/result');
  }

  getBusStopUI() {
    if (!this.state.busRouteStates || !Object.keys(this.state.busRouteStates).length) {
      return <p>No bus stops found in this map.</p>;
    }

    return (
      <div>
        <ul className="no-bullets">
          <li>
            <label className="control control-xl checkbox">
              <input type="checkbox"
                checked={Object.keys(this.state.busRouteStates).every(key => this.state.busRouteStates[key])}
                onChange={this.handleAllBusesToggle}/>
              <span className="control-indicator"></span>
              <span className="control-label">Bus stops</span>
            </label>
          </li>
          <li>
            <ul className="no-bullets">
              {Object.keys(this.state.busRouteStates).map(ref => (
                <li>
                  <label className="control control-xl checkbox">
                    <input type="checkbox" name="busroutes" value={ref}
                      checked={this.state.busRouteStates[ref]}
                      onChange={this.handleBusToggle}/>
                    <span className="control-indicator"></span>
                    <span className="control-label">{ref}</span>
                  </label>
                </li>
              ))}
            </ul>
          </li>
        </ul>
      </div>
    );
  }

  handleAllBusesToggle(event) {
    let busRouteStates = Object.assign({}, this.state.busRouteStates);
    Object.keys(busRouteStates).forEach(key => busRouteStates[key] = event.target.checked);
    this.setState({busRouteStates});
  }

  handleBusToggle(event) {
    let busRouteStates = Object.assign({}, this.state.busRouteStates);
    busRouteStates[event.target.value] = event.target.checked;
    this.setState({busRouteStates});
  }

  getRouteStates(busStops) {
    let routes = this.getRoutes(busStops);
    let routeStates = {};
    routes.forEach(route => routeStates[route] = false);
    return routeStates;
  }

  getRoutes(busStops) {
    let routes = new Set();
    Object.keys(busStops).forEach(key => {
      let busStop = busStops[key];
      busStop.busRoutes.forEach(route => {
        routes.add(route.ref);
      })
    });
    return routes;
  }
}

export default withRouter(MapDesigner);