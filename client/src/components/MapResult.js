import React, { Component } from 'react';
import MapPreview3D from './MapPreview3D';
import { Link } from 'react-router-dom';

class MapResult extends Component {
  constructor(props) {
    super(props);
    this.state = {
      nearbyLocations: null
    };
    this.service = new window.google.maps.places.PlacesService(document.createElement('div'));
  }

  componentDidMount() {
    let bounds = new window.google.maps.LatLngBounds(
      new window.google.maps.LatLng(
        this.props.data.minLat,
        this.props.data.minLng,
      ),
      new window.google.maps.LatLng(
        this.props.data.maxLat,
        this.props.data.maxLng
      )
    );
    this.service.nearbySearch({bounds}, (results, status) => {
      if (status == window.google.maps.places.PlacesServiceStatus.OK) {
        if (results.length > 5) {
          results = results.slice(0, 5);
        }
        this.setState({
          nearbyLocations: results
        });
      }
    });
  }

  render() {
    let stlId = this.props.stlId;
    return (
      <div className="container">
        <nav className="nav-inline">
          <ul>
            {!this.props.highContrast ? (
              <li><a role="button" tabindex="0" onClick={() => this.props.setHighContrast(true)}>View page in high contrast</a></li>
            ) : (
              <li><a role="button" tabindex="0" onClick={() => this.props.setHighContrast(false)}>View page without high contrast</a></li>
            )}  
            <li><Link to="/design">Back to map design</Link></li>
            <li><Link to="/">Back to location search</Link></li>
          </ul>
        </nav>
        <div className="header">
          <h2 className="header-title">3D Map Preview</h2>
          {this.state.nearbyLocations && (
            <div>
              <p>Places that appear within the bounds of the map:</p>
              <ul>
                {this.state.nearbyLocations.map(location => (
                  <li key={location.id}>{location.name}</li>
                ))}
              </ul>
            </div>
          )}
          {this.props.data.mapCreated && stlId ? (
            <div>
              <p>Rotate the map preview using the arrow keys or by using the buttons below the map.</p>
              <MapPreview3D mapStlUrl={`/api/map/${stlId}/stl`} />
              <a download href={`/api/map/${stlId}/stl`} className="button button-l">Download map file</a>
            </div>
          ) : (
            <div>
              <p>Map is loading, please wait...</p>
              <div className="spinner" style={{'width': '680px', 'height': '500px', 'border': '1px solid black'}}/>
            </div>
          )}
        </div>
      </div>
    );
  }
}

// var downloadFile = function() {
//   window.URL = window.webkitURL || window.URL;

//   var prevLink = output.querySelector('a');
//   if (prevLink) {
//     window.URL.revokeObjectURL(prevLink.href);
//     output.innerHTML = '';
//   }

//   var bb = new Blob([typer.textContent], {type: MIME_TYPE});

//   var a = document.createElement('a');
//   a.download = container.querySelector('input[type="text"]').value;
//   a.href = window.URL.createObjectURL(bb);
//   a.textContent = 'Download ready';

//   a.dataset.downloadurl = [MIME_TYPE, a.download, a.href].join(':');
//   a.draggable = true; // Don't really need, but good practice.
//   a.classList.add('dragout');

//   output.appendChild(a);

//   a.onclick = function(e) {
//     if ('disabled' in this.dataset) {
//       return false;
//     }

//     cleanUp(this);
//   };
// };

export default MapResult;