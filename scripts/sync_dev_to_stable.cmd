xcopy /y /s sma-em-dev sma-em
sed -i 's/sma-em-dev/sma-em/g' sma-em/config.yaml
sed -i 's/ (developer version)//' sma-em/config.yaml
sed -i 's/ (developer version)//' sma-em/README.md
sed -i 's/ (developer version)//' sma-em/DOCS.md
