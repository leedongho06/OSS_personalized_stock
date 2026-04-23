import click
import profile_io

@click.group()
def cli():
    """주식 추천 CLI 시스템"""
    pass

@cli.command()
def profile():
    """사용자 투자 성향 입력 및 갱신"""
    click.echo("--- 사용자 프로파일 설정 ---")
    
    risk_tolerance = click.prompt("투자 성향을 입력하세요 (안전/중립/공격)", type=str)
    capital = click.prompt("투자 예정 금액을 입력하세요 (단위: 만원)", type=int)
    
    user_data = {
        "risk_tolerance": risk_tolerance,
        "capital": capital
    }
    
    profile_io.save_profile(user_data)
    click.echo("\n프로파일이 성공적으로 저장되었습니다. (user_profile.json)")

@cli.command()
def recommend():
    """저장된 프로파일 기반 주식 추천 실행 (현재 더미 데이터)"""
    user_data = profile_io.load_profile()
    
    if not user_data:
        click.echo("저장된 프로파일이 없습니다. 'python main.py profile'을 먼저 실행하여 프로파일을 생성하세요.")
        return
        
    click.echo(f"\n[{user_data['risk_tolerance']}] 성향과 [{user_data['capital']}만원] 자본금 기반으로 종목을 분석합니다...")
    click.echo("\n[시스템: 알고리즘 모듈 미연동 - 더미 데이터 출력]")
    click.echo("추천 종목 1: 삼성전자")
    click.echo("추천 종목 2: 현대차")

if __name__ == '__main__':
    cli()
