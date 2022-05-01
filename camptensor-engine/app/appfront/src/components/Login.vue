<template>
  <div>
    <img :src="background" class="illustration" />
    <el-row class="my-auth">
      <el-form ref="loginForm" :model="user" status-icon label-width="80px">
        <el-form-item prop="username" label="用户名" class="label-name">
          <el-input
            v-model="user.username"
            placeholder="请输入用户名"
            prefix-icon
          ></el-input>
        </el-form-item>
        <el-form-item
          id="password"
          prop="password"
          label="密码"
          class="label-name"
        >
          <el-input
            v-model="user.password"
            show-password
            placeholder="请输入密码"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <button class="auth-button" @click.prevent="doLogin()">登 录</button>
        </el-form-item>
      </el-form>
    </el-row>
  </div>
</template>

<script>
import { saveToken } from "../utils";
export default {
  name: "login",
  data() {
    return {
      user: {
        username: "",
        password: ""
      },
      background: require("@/assets/illustration.png")
    };
  },
  created() {},
  methods: {
    doLogin() {
      if (!this.user.username) {
        this.$message.error("请输入用户名！");
        return;
      } else if (!this.user.password) {
        this.$message.error("请输入密码！");
        return;
      } else {
        const payload = {
          username: this.user.username,
          password: this.user.password
        };
        this.$request
          .post(`${this.$store.state.endpoints.jwtauth}/obtain_token/`, payload)
          .then(response => {
            saveToken(response.data);
          })
          .catch(error => {
            console.log(error);
            if (error.response) {
              if (error.response.status == 401) {
                this.$message.error("验证未通过, 登录失败");
              }
            } else if (error.request) {
              console.log(error.request);
            } else {
              this.$message.error(error.message);
            }
          });
      }
    }
  }
};
</script>

<style scoped>
#password {
  margin-bottom: 5px;
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
h3 {
  color: #0babeab8;
  font-size: 24px;
}

hr {
  background-color: #444;
  margin: 20px auto;
}

a {
  text-decoration: none;
  color: #aaa;
  font-size: 15px;
}

a:hover {
  color: coral;
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
  margin-top: 15px;
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
