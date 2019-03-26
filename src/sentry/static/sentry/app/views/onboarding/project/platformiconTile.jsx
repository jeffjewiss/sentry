import PropTypes from 'prop-types';
import React from 'react';
import classnames from 'classnames';
import styled, {css} from 'react-emotion';

// [platformName => [background, forground]
const platformColors = [
  ['python', ['#3060b8']],
  ['python-django', ['#57be8c']],
  ['javascript', ['#ecd744', '#111']],
  ['javascript-react', ['#2d2d2d', '#00d8ff']],
  ['javascript-ember', ['#ed573e', '#fff']],
  ['ruby', ['#e03e2f', '#fff']],
  ['rails', ['#e03e2f', '#fff']],
  ['javascript-angular', ['#e03e2f', '#fff']],
  ['java', ['#ec5e44']],
  ['php', ['#6c5fc7']],
  ['node', ['#90c541']],
  ['app-engine', ['#ec5e44']],
  ['csharp', ['#638cd7']],
  ['go', ['#fff', '#493e54']],
  ['elixir', ['#4e3fb4']],
];

const getColorStyles = props =>
  !props.monoTone &&
  css`
    background: #625471;
    color: #fff;

    ${platformColors.map(
      ([platform, [bg, fg]]) => css`
        &.${platform} {
          ${bg && `background: ${bg}`};
          ${fg && `color: ${fg}`};
        }
      `
    )};
  `;

const getIconOverrides = props => css`
  &.python-pylons:before,
  &.python-celery:before,
  &.python-awslambda:before,
  &.python-pyramid:before,
  &.python-tornado:before,
  &.python-rq:before,
  &.python-sanic:before {
    content: '\\e602';
  }

  &.javascript-backbone:before,
  &.javascript-vue:before {
    content: '\\e600';
  }

  &.ruby-rack:before {
    content: '\\e604';
  }

  &.java-log4j:before,
  &.java-log4j2:before,
  &.java-logback:before {
    content: '\\e608';
  }

  &.php-symfony2:before,
  &.php-monolog:before {
    content: '\\e601';
  }

  &.node-express:before,
  &.node-connect:before,
  &.node-koa:before {
    content: '\\e609';
  }

  &.go-http:before {
    content: '\\e606';
  }
`;

const PlatformiconTile = styled(({platform, className}) => (
  <div
    className={classnames(
      className,
      'platformicon',
      `platformicon-${platform}`,
      platform.split('-')[0],
      platform
    )}
  />
))`
  ${getIconOverrides};
  ${getColorStyles};
`;

PlatformiconTile.propTypes = {
  platform: PropTypes.string,
  className: PropTypes.string,
  monoTone: PropTypes.bool,
};

export default PlatformiconTile;
