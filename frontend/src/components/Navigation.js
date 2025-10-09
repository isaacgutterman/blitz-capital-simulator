import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

const Sidebar = styled.nav`
  position: fixed;
  left: 0;
  top: 0;
  width: 250px;
  height: 100vh;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 0;
  z-index: 1000;
`;

const Logo = styled.div`
  padding: 0 20px 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 30px;
`;

const LogoText = styled.h1`
  color: white;
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const NavList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const NavItem = styled.li`
  margin: 0;
`;

const NavLink = styled(Link)`
  display: block;
  padding: 15px 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  
  &:hover {
    color: white;
    background: rgba(255, 255, 255, 0.1);
    border-left-color: #4ecdc4;
  }
  
  &.active {
    color: white;
    background: rgba(255, 255, 255, 0.15);
    border-left-color: #ff6b6b;
  }
`;

const NavIcon = styled.span`
  margin-right: 10px;
  font-size: 18px;
`;

function Navigation() {
  return (
    <Sidebar>
      <Logo>
        <LogoText>Blitz Capital</LogoText>
      </Logo>
      <NavList>
        <NavItem>
          <NavLink to="/">
            <NavIcon>📊</NavIcon>
            Dashboard
          </NavLink>
        </NavItem>
        <NavItem>
          <NavLink to="/algorithms">
            <NavIcon>🤖</NavIcon>
            Algorithms
          </NavLink>
        </NavItem>
      </NavList>
    </Sidebar>
  );
}

export default Navigation;
