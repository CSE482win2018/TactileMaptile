import React, { Component } from 'react';

import Home from './components/Home';
import MapDesigner from './components/MapDesigner';
import MapPreviewOl from './components/MapPreviewOl';
import { Route, Switch, withRouter } from 'react-router-dom';

import normalTheme from './App.css';
import highContrastTheme from './AppHighContrast.css';
import './turret.css';

class App extends Component {
  constructor(props) {
    super(props);
    let params = new URLSearchParams(props.location.search);
    this.state = {
      data: {
        address: null,
        offsetX: null,
        offsetY: null,
        size: 17,
        scale: 2400
      },
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
    this.updateData = this.updateData.bind(this);
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
            <Route path="/" exact render={(props) => <Home {...props} data={this.state.data} updateData={this.updateData} highContrast={this.state.highContrast} setMapAddress={this.setMapAddress}/>}/>
            <Route path="/design" render={(props) => <MapDesigner {...props} data={this.state.data} updateData={this.updateData} highContrast={this.state.highContrast} address={this.state.address}/>}/>
            <Route path="/map" render={(props) => <MapPreviewOl {...props} data={this.state.data} updateData={this.updateData}/>}/>
          </Switch>
        </div>
      </main>
    );
  }

  setMapAddress(result) {
    console.log("chosen address: ", result);
    setTimeout(() => this.props.history.push('/design'), 1);
  }

  updateData(data) {
    console.log("updating data:", data);
    let updatedData = {...this.state.data, data};
    this.setState({
      data: updatedData
    })
  }

  
}

export default withRouter(App);
