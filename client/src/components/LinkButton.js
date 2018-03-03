import React, { Component } from 'react';

class LinkButton extends Component {

  constructor(props) {
    super(props);

    this.handleClick = this.handleClick.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
    this.toggleButton = this.toggleButton.bind(this);
  }

  render() {
    return (
      <a role="button" tabIndex="0" onClick={this.handleClick} onKeyPress={this.handleKeyPress}>
        {this.props.children}
      </a>
    );
  }

  handleClick(event) {
    this.toggleButton(event);
  }

  handleKeyPress(event) {
    // Check to see if space or enter were pressed
    if (event.key === " " || event.key === "Enter") {
      // Prevent the default action to stop scrolling when space is pressed
      event.preventDefault();
      this.toggleButton(event);
    }
  }

  toggleButton(event) {
    this.props.onClick(event);
  }
}

export default LinkButton;
