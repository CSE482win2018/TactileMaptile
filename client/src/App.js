import React, { Component } from 'react';

import Home from './components/Home';
import MapDesigner from './components/MapDesigner';
import MapPreviewOl from './components/MapPreviewOl';
import MapResult from './components/MapResult';
import SearchResults from './components/SearchResults';
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
        offsetX: 0,
        offsetY: 0,
        size: 17,
        scale: 2400,
        minLat: null,
        maxLat: null,
        minLng: null,
        maxLng: null,
        locationInput: null,
        searchResults: null
      },
      stlId: null,
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

    this.updateData = this.updateData.bind(this);
    this.setStlId = this.setStlId.bind(this);
    this.navigateToMapResult = this.navigateToMapResult.bind(this);
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
            <Route path="/" exact render={(props) => <Home {...props} data={this.state.data} updateData={this.updateData} highContrast={this.state.highContrast} setSearchResults={this.setSearchResults}/>}/>
            <Route path="/design" render={(props) => <MapDesigner {...props} data={this.state.data} setStlId={this.setStlId} navigateToMapResult={this.navigateToMapResult} updateData={this.updateData} highContrast={this.state.highContrast}/>}/>
            <Route path="/searchresults" render={(props) => <SearchResults {...props} data={this.state.data} updateData={this.updateData}/>}/>
            <Route path="/result" render={(props) => <MapResult {...props} data={this.state.data} stlId={this.state.stlId} updateData={this.updateData} highContrast={this.state.highContrast}/>}/>
            <Route path="/map" render={(props) => <MapPreviewOl {...props} data={this.state.data} updateData={this.updateData}/>}/>
          </Switch>
        </div>
      </main>
    );
  }

  updateData(data) {
    console.log("updating data:", data);
    let updatedData = {...this.state.data, ...data};
    console.log(updatedData);
    this.setState({
      data: updatedData
    })
  }

  setStlId(id) {
    this.setState({
      stlId: id
    });
  }

  navigateToMapResult() {
    setTimeout(() => this.props.history.push('/result'), 1);
  }

}

export default withRouter(App);
