<template>
  <el-container id="app" direction="vertical">
    <Header id="header"></Header>
    <el-container>
      <Navbar id="navbar"></Navbar>
      <Main id="main"></Main>
    </el-container>
    <!-- <Footer />  -->
  </el-container>
</template>

<script>
import Header from './components/layout/Header.vue'
import Main from './components/layout/Main.vue'
import Navbar from './components/layout/Navbar.vue'
import Footer from './components/layout/Footer.vue'
export default {
  components: { Header, Main, Navbar, Footer },
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
html,body,.el-container {
  height: 100%;
}

body {
  margin: 0px;
}

</style>
