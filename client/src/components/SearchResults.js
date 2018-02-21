import React, { Component } from 'react';
import { Redirect, Link } from 'react-router-dom';
import MapPreviewOl from './MapPreviewOl';

class SearchResults extends Component {
  constructor(props) {
    super(props);

    let currAddressIndex = null;
    if (props.data.searchResults.length === 1) {
      currAddressIndex = 0;
    }
    
    this.state = {
      currAddressIndex: currAddressIndex,
      showFormError: false
    }

    this.handleMultipleResultsSelect = this.handleMultipleResultsSelect.bind(this);
    this.handleAddressSubmit = this.handleAddressSubmit.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    let currAddressIndex = null;
    if (nextProps.data.searchResults.length === 1) {
      currAddressIndex = 0;
    }
    console.log("set state:", currAddressIndex);
    this.setState({
      currAddressIndex: currAddressIndex
    });
  }

  render() {
    let {searchResults, locationInput} = this.props.data;
    if (!searchResults) {
      return <Redirect to="/"/>
    }

    return (
      <div className="row-container">
        <div className="container">
          <nav className="nav-inline">
            <ul>
              <li><Link to="/">Back to home</Link></li>
            </ul>
          </nav>
          <div className="header">
            <h2 className="header-title">Search Results</h2>
          </div>
          <p>You searched: {locationInput}</p>
          {this.getSearchResultsUI(searchResults)}
        </div>
        <div>
          {this.state.currAddressIndex !== null && <MapPreviewOl maxSize={500} data={this.props.data} address={this.props.data.searchResults[this.state.currAddressIndex]}/>}
        </div>
      </div>
    )
  }

  getSearchResultsUI(searchResults) {
    if (searchResults.length === 1) {
      let address = searchResults[0];
      return (
        <div>
          <fieldset>
            <legend>Confirm address</legend>
            <p>Found 1 results. Hit "OK" if this is the address you want, otherwise try searching again.</p>
            <p>Address found: {address.formatted_address}</p>
            <form onSubmit={this.handleAddressSubmit}>
              <button type="submit" className={"button swatch color-white background-secondary"}>OK</button>
            </form>
          </fieldset>
        </div>
      );
    } else {
      if (searchResults.length > 5) {
        searchResults = searchResults.slice(0, 5);
      }
      return (
        <div>
          <form onSubmit={this.handleAddressSubmit}>
            <p>Found {searchResults.length} results. Choose the correct address below and hit "OK", otherwise try searching again.</p>
            <fieldset>
              <legend>Choose an address</legend>
              {searchResults.map((result, index) => (
                <label className="control control-l radio" key={index}>
                  <input type="radio" name="address" value={index} onChange={this.handleMultipleResultsSelect}/>
                  <span className="control-indicator"/>
                  <span className="control-label">{result.formatted_address}</span>
                </label>
              ))}
            <button type="submit" className={"button swatch color-white background-secondary"}>OK</button>
            {this.state.showFormError && (
              <p className="form-message error">Choose one of the addresses before hitting "OK"</p>
            )}
            </fieldset>
          </form>
        </div>
      );
    }
  }
  
  handleAddressSubmit(event) {
    event.preventDefault();
    if (this.state.currAddressIndex === null) {
      this.setState({showFormError: true});
      return;
    }
    this.props.updateData({address: this.props.data.searchResults[this.state.currAddressIndex]});
    this.props.history.push('/design');
  }

  handleMultipleResultsSelect(event) {
    this.setState({currAddressIndex: +event.currentTarget.value});
  }
}

export default SearchResults;