import React, { Component } from 'react';

import Home from './Home';
import MapDesigner from './MapDesigner';
import { Route, Switch, withRouter } from 'react-router-dom';

import normalTheme from './App.css';
import highContrastTheme from './AppHighContrast.css';
import './turret.css';

class App extends Component {
  constructor(props) {
    super(props);
    let params = new URLSearchParams(props.location.search);
    this.state = {
      address: null,
      theme: null,
      highContrast: params.has('highContrast')
    };

    this.contentClassNames = {
      normal: {
        main: "",
        header: "header-title background-primary color-white"
      },
      highContrast: {
        main: "background-black color-white",
        header: "header-title"
      }
    }

    this.setMapAddress = this.setMapAddress.bind(this);
  }

  componentDidUpdate(prevProps, prevState) {
    let params = new URLSearchParams(this.props.location.search);
    let highContrast = params.has('highContrast');
    if (prevState.highContrast === highContrast) {
      return;
    }
    this.setState({highContrast})
  }

  render() {
    let classNames = this.state.highContrast ? this.contentClassNames.highContrast : this.contentClassNames.normal;
    return (
      <main role="main" className={classNames.main}>
        <header className={classNames.header}>
          <h1 className="header-title color-white">
            TactileMaptile
          </h1>
        </header>
        <div>
          <Switch>
            <Route path="/" exact render={(props) => <Home {...props} highContrast={this.state.highContrast} setMapAddress={this.setMapAddress}/>}/>
            <Route path="/design" render={(props) => <MapDesigner {...props} highContrast={this.state.highContrast} address={this.state.address}/>}/>
          </Switch>
        </div>
      </main>
    );
  }

  setMapAddress(result) {
    this.setState({
      address: result
    });
    console.log("chosen address: ", result);
    setTimeout(() => this.props.history.push('/design'), 1);
  }
}

export default withRouter(App);
