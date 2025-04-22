const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const BundleTracker = require("webpack-bundle-tracker");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const Dotenv = require("dotenv-webpack");

module.exports = (env, argv) => {
  const isDev = argv.mode === "development";

  return {
    mode: isDev ? "development" : "production",
    devtool: isDev ? "source-map": "source-map",
    entry: {
      index: "./js/index",
    },
    output: {
      path: path.resolve("webpack_bundles/"),
      publicPath: isDev ? "https://localhost:3000/frontend/webpack_bundles/" : "/static/",
      filename: isDev ? "[name].js" : "[name]-[chunkhash].js",
    },
    devServer: {
      hot: true,
      historyApiFallback: true,
      host: "0.0.0.0",
      port: 443,
      headers: {
        "Access-Control-Allow-Origin": "*" ,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS"
      },
      server: {
        type: "https",
        options: {
          key: "/project/.certs/localhost-key.pem",
          cert: "/project/.certs/localhost.pem",
          ca: "/home/$USER/.local/share/mkcert/rootCA.pem"
        },
      },
      allowedHosts: "all",
      client: {
        overlay: false, // Prevent error overlay popups
      },

    },
    module: {
      rules: [
        {
          test: /\.(js|jsx|ts|tsx)$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader",
            options: {
              presets: ["@babel/preset-env", "@babel/preset-react", "@babel/preset-typescript"],
            },
          },
        },
        {
          test: /\.s?css$/,
          use: [
            MiniCssExtractPlugin.loader,
            {
              loader: "css-loader",
              options: {
                sourceMap: isDev,
              },
            },
            {
              loader: "sass-loader",
              options: {
                sourceMap: isDev,
              },
            },
          ],
        },
        {
          test: /\.(png|jpg|jpeg|gif|svg|webp)$/,
          exclude: /node_modules/,
          type: "asset/resource",
          generator: {
            filename: "images/[hash][ext][query]",
          },
        },
        {
          test: /\.(woff(2)?|eot|ttf|otf)$/,
          exclude: /node_modules/,
          type: "asset/resource",
          generator: {
            filename: "fonts/[hash][ext][query]",
          },
        },
      ],
    },
    plugins: [
      //new ForkTsCheckerWebpackPlugin(),
      new Dotenv(),

      new BundleTracker({
        path: path.resolve(__dirname),
        filename: "webpack-stats.json",
      }),
      new MiniCssExtractPlugin({
        filename: isDev ? "[name].css" : "[name]-[contenthash].css",
      }),
      new HtmlWebpackPlugin({
        favicon: "assets/favicon.ico",
      }),
    ],
    resolve: {
      extensions: [".js", ".jsx", ".ts", ".tsx"],
      alias: {
        "@": path.resolve("js"),
      },
      fallback: {
        process: require.resolve("process/browser"),
        path: false,
        fs: false,
      }
    },
    optimization: {
      splitChunks: {
        chunks: "all",
      },
    },
  };
};
