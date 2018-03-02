import React, { Component } from 'react';
import * as THREE from 'three';
import '../App.css';
import '../turret.css';

var STLLoader = require('three-stl-loader')(THREE);

class MapPreview3D extends Component {
  constructor(props) {
    super(props);
    console.log(THREE);
    this.show3dPreview = this.show3dPreview.bind(this);
    this.rotate = this.rotate.bind(this);
    this.render3D = this.render3D.bind(this);
    this.onKeyPressed = this.onKeyPressed.bind(this);
  }

  componentDidMount() {
    this.show3dPreview();
  }

  render() {
    return (
      <div>
        <div tabIndex="0" onKeyDown={this.onKeyPressed} style={{'width': '680px', 'height': '500px'}} ref={(element) => { this.element = element; }} />
        <button onClick={() => this.rotate(0, 0, -0.1)}>Rotate clockwise</button>
        <button onClick={() => this.rotate(0, 0, 0.1)}>Rotate counterclockwise</button>
        <button onClick={() => this.rotate(0.1, 0, 0)}>Tilt forward</button>
        <button onClick={() => this.rotate(-0.1, 0, 0)}>Tilt backward</button>
      </div>
    );
  }

  onKeyPressed(e) {
    switch (e.keyCode) {
      case 37:
        this.rotate(0, 0, 0.1);
        break;
      case 38:
        this.rotate(-0.1, 0, 0);
        break;
      case 39:
        this.rotate(0, 0, -0.1);
        break;
      case 40:
        this.rotate(0.1, 0, 0);
        break;
    }
  }

  rotate(x, y, z) {
    this.mesh.rotation.x += x;
    this.mesh.rotation.y += y;
    this.mesh.rotation.z += z;
    this.render();
  }

  render3D() {
    requestAnimationFrame(this.render3D);
    this.renderer.render(this.scene, this.camera);
  }

  show3dPreview() {
    let element = this.element;
    let width = element.offsetWidth;
    let height = element.offsetHeight;
    // elem.append("<p class='loading-3d-preview'>Loading 3D preview...</p>");
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(width, height);
    this.renderer.setClearColor( 0xaaaaaa, 1 );
    // renderer.shadowMap.enabled = true; // doesn't work on an old machine if I enable shadows
    // renderer.shadowMapType = THREE.PCFSoftShadowMap;

    var loader = new STLLoader();
    loader.load(this.props.mapStlUrl, ( geometry ) => {
      // Mesh
      this.mesh = new THREE.Mesh(geometry, new THREE.MeshLambertMaterial( { color: 0x9975B9 } ) );
      this.mesh.rotation.x = Math.PI * 1.5 + Math.PI / 4;
      this.mesh.castShadow = true;
      this.mesh.receiveShadow = true;

      // Lights
      var dirLight = new THREE.DirectionalLight(0xfffbf4, 0.85);
      dirLight.position.set(100, 100, 100);
      // dirLight.castShadow = true;
      // dirLight.shadowMapWidth = 2048; // default is 512
      // dirLight.shadowMapHeight = 2048; // default is 512
      var ambLight = new THREE.AmbientLight(0x404050);

      // Camera
      this.camera = new THREE.PerspectiveCamera(25, width / height, 0.1, 0);
      geometry.computeBoundingBox();  // otherwise geometry.boundingBox will be undefined
      var diameter = Math.max(geometry.boundingBox.max.x, geometry.boundingBox.max.y);
      this.camera.position.z = diameter * 2.375;
      // camera.position.y = camera.position.z * -0.04;

      // Center geometry into the origin
      geometry.translate(- diameter / 2, - diameter / 2, 0);

      // Scene
      this.scene = new THREE.Scene();
      this.scene.add(dirLight);
      this.scene.add(ambLight);
      this.scene.add(this.mesh);

      // Replace "Loading..." with renderer
      element.innerHTML = "";
      element.appendChild(this.renderer.domElement);
      this.render3D();
    });
  };
}

export default MapPreview3D;