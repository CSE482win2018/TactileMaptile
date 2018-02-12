import React, { Component } from 'react';

import Home from './Home';
import MapDesigner from './MapDesigner';
import { Route, withRouter } from 'react-router-dom';

import './App.css';
import './turret.css';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      address: null
    };

    this.setMapAddress = this.setMapAddress.bind(this);
  }

  render() {
    return (
      <main role="main">
        <header className="header background-primary">
          <h1 className="header-title color-white">
            TactileMaptile
          </h1>
        </header>
        <div>
          <Route path="/" exact render={() => <Home setMapAddress={this.setMapAddress}/>}/>
          <Route path="/design" render={() => <MapDesigner address={this.state.address}/>}/>
        </div>
      </main>
    );
  }

  setMapAddress(result) {
    this.setState({
      address: result
    });
    console.log("chosen address: ", result);
    setTimeout(() => this.props.history.push('/design'), 3);
  }
}

export default withRouter(App);
