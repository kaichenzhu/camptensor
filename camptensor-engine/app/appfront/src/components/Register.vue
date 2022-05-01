<template>
  <div>
    <img :src="background" class="illustration" />
    <el-row class="my-auth">
      <el-form ref="loginForm" :model="user" status-icon label-width="80px">
        <el-form-item prop="username" label="用户名" class="label-name">
          <el-input v-model="user.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item prop="email" label="邮箱" class="label-name">
          <el-input v-model="user.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item prop="password" label="设置密码" class="label-name">
          <el-input v-model="user.password" show-password placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item prop="password2" label="设置密码" class="label-name">
          <el-input v-model="user.password2" show-password placeholder="再次输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <button class="auth-button" @click.prevent="doRegister()">注册账号</button>
        </el-form-item>
      </el-form>
    </el-row>
  </div>
</template>

<script>
  import { saveToken } from '../utils'
  export default {
    name: "register",
    data() {
      return {
        user: {
          username: "",
          email: "",
          password: ""
        },
        background: require("@/assets/illustration.png")
      };
    },
    created() {
      // console.log($);
      // console.log("1111");
    },
    methods: {
      doRegister() {
        if (!this.user.username) {
          this.$message.error("请输入用户名！");
          return;
        } else if (!this.user.email) {
          this.$message.error("请输入邮箱！");
          return;
        } else if (this.user.email != null) {
          var reg = /^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/;
          if (!reg.test(this.user.email)) {
            this.$message.error("请输入有效的邮箱！");
          } else if (!this.user.password || !this.user.password2) {
            this.$message.error("请输入密码！");
            return;
          } else if (this.user.password != this.user.password2) {
            this.$message.error("密码不一致！");
            return;
          } else {
            // this.$router.push({ path: "/" }); //无需向后台提交数据，方便前台调试
            this.$request.post(`${this.$store.state.endpoints.jwtauth}/register/`, {
              username: this.user.username,
              email: this.user.email,
              password: this.user.password
            })
            .then(response => {
              // console.log("输出response.data", res.data);
              // console.log("输出response.data.status", res.data.status);
              if (response.status === 201) {
                saveToken(response.data);
                this.$router.push({
                  name: 'Login'
                })
              }
            });
          }
        }
      }
    }
  }

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  h3 {
    color: #0babeab8;
    font-size: 24px;
  }

  hr {
    background-color: #444;
    margin: 20px auto;
  }

  .el-button {
    width: 80%;
    margin-left: -50px;
  }

  .illustration {
  width: 40%;
  height: 100%;
  position: fixed;
  margin: auto;
  left: 0;
  top: 0;
  bottom: 0;
}

.my-auth {
  width: 25%;
  height: 20%;
  margin: auto;
  left: 30%;
  top: 0;
  bottom: 10%;
  right: 0;
  position: absolute;
}
.label-name {
  font-weight: bold;
}

.auth-button {
  background-color: #0a6bff;
  border-radius: 4px;
  border: 0;
  box-shadow: rgba(1, 60, 136, 0.5) 0 -1px 3px 0 inset,
    rgba(0, 44, 97, 0.1) 0 3px 6px 0;
  box-sizing: border-box;
  color: #fff;
  cursor: pointer;
  display: inherit;
  font-family: "Space Grotesk", -apple-system, system-ui, "Segoe UI", Roboto,
    Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji",
    "Segoe UI Symbol";
  font-size: 18px;
  font-weight: 700;
  line-height: 24px;
  margin-top: 10px;
  min-height: 56px;
  min-width: 120px;
  padding: 16px 20px;
  position: relative;
  text-align: center;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  vertical-align: baseline;
  transition: all 0.2s cubic-bezier(0.22, 0.61, 0.36, 1);
}

.auth-button:hover {
  background-color: #065dd8;
}

@media (min-width: 768px) {
  .auth-button {
    padding: 16px 44px;
    min-width: 100%;
  }
}
</style>
