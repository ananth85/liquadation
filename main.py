#!/usr/bin/env python3
"""
Liquidation Document Generation Agent - Main CLI Interface
Multi-Agent Control Plane (MCP) for synthetic liquidation document generation
"""

import asyncio
import click
import logging
import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.supervisor_agent import SupervisorAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('liquidation_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global supervisor instance
supervisor: Optional[SupervisorAgent] = None

async def initialize_supervisor():
    """Initialize the supervisor agent with configuration"""
    global supervisor
    
    abn_api_key = os.getenv('ABN_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    config = {
        'abn_api_key': abn_api_key,
        'openai_api_key': openai_api_key,
        'templates_folder': "templates",
        'output_dir': "output_pdfs",
        'sample_folder': "sample"
    }
    
    supervisor = SupervisorAgent(config=config, logger=logger)
    
    # Perform health check
    health = await supervisor.health_check()
    logger.info(f"System health check: {health['supervisor']['status']}")
    
    for agent_name, agent_health in health['agents'].items():
        if agent_health['status'] != 'healthy':
            logger.warning(f"Agent {agent_name}: {agent_health['status']} - {', '.join(agent_health['issues'])}")

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug):
    """Liquidation Document Generation Agent - MCP-based synthetic document generator"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

@cli.command()
@click.argument('prompt', required=True)
@click.option('--output-dir', '-o', default='output_pdfs', help='Output directory for PDFs')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'summary']), help='Output format')
def prompt(prompt, output_dir, output_format):
    """Generate liquidation documents from a free-form prompt
    
    Example:
    python main.py prompt "Generate liquidation docs for a fintech startup in Sydney with debt issues"
    """
    async def run():
        await initialize_supervisor()
        
        try:
            click.echo(f"🤖 Generating liquidation documents from prompt...")
            click.echo(f"📝 Prompt: {prompt}")
            
            result = await supervisor.generate_from_prompt(prompt)
            
            if result['success']:
                company_data = result.get('company_data', {})
                documents = result.get('documents', [])
                
                company_name = company_data.get('company_name', 'Generated Company')
                company_abn = company_data.get('abn', 'Unknown')
                
                click.echo(f"✅ Successfully generated documents for: {company_name}")
                click.echo(f"📊 Company ABN: {company_abn}")
                click.echo(f"📄 Generated {len([d for d in documents if d.get('success', False)])} documents:")
                
                for doc in documents:
                    if doc.get('success', False):
                        filename = doc.get('pdf_result', {}).get('filename', 'Generated file')
                        doc_type = doc.get('document_type', 'liquidation_document')
                        click.echo(f"   • {doc_type}: {filename}")
                
                if output_format == 'json':
                    output_file = Path(output_dir) / f"generation_result_{result['pipeline_id']}.json"
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2, default=str)
                    click.echo(f"📋 Full results saved to: {output_file}")
                
            else:
                click.echo("❌ Generation failed", err=True)
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            raise click.Abort()
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.argument('csv_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output_pdfs', help='Output directory for PDFs')
def csv(csv_path, output_dir):
    """Generate liquidation documents from CSV file
    
    CSV should contain columns like: company_name, abn, acn, email, etc.
    
    Example:
    python main.py csv data/companies.csv
    """
    async def run():
        await initialize_supervisor()
        
        try:
            click.echo(f"📊 Processing CSV file: {csv_path}")
            
            result = await supervisor.generate_from_csv(csv_path)
            
            if result['success']:
                click.echo(f"✅ Successfully processed {result['processed_records']} companies")
                
                successful_docs = 0
                failed_docs = 0
                
                for company_result in result['generated_documents']:
                    if 'error' in company_result:
                        failed_docs += 1
                        company_name = company_result['company_data'].get('company_name', 'Unknown')
                        click.echo(f"❌ Failed: {company_name} - {company_result['error']}")
                    else:
                        successful_docs += 1
                        company_name = company_result['company_data']['company_name']
                        doc_count = len([d for d in company_result['documents'] if d['success']])
                        click.echo(f"✅ {company_name}: {doc_count} documents generated")
                
                click.echo(f"📈 Summary: {successful_docs} successful, {failed_docs} failed")
                
                # Save results
                output_file = Path(output_dir) / f"csv_generation_{result['pipeline_id']}.json"
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"📋 Full results saved to: {output_file}")
                
            else:
                click.echo("❌ CSV processing failed", err=True)
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            raise click.Abort()
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.argument('abn', required=True)
@click.option('--output-dir', '-o', default='output_pdfs', help='Output directory for PDFs')
def abn(abn, output_dir):
    """Generate liquidation documents from ABN lookup
    
    Example:
    python main.py abn 12345678901
    """
    async def run():
        await initialize_supervisor()
        
        try:
            click.echo(f"🔍 Looking up ABN: {abn}")
            
            result = await supervisor.generate_from_abn(abn)
            
            if result['success']:
                company_data = result['company_data']
                documents = result['documents']
                
                click.echo(f"✅ Found company: {company_data.get('entity_name', 'Unknown')}")
                click.echo(f"🏢 Entity type: {company_data.get('entity_type', 'Unknown')}")
                click.echo(f"📍 Address: {company_data.get('address', {}).get('state', 'Unknown')}")
                
                successful_docs = len([d for d in documents if d['success']])
                click.echo(f"📄 Generated {successful_docs} documents:")
                
                for doc in documents:
                    if doc['success']:
                        filename = doc['pdf_result']['filename']
                        click.echo(f"   • {doc['document_type']}: {filename}")
                
                # Save results
                output_file = Path(output_dir) / f"abn_generation_{result['pipeline_id']}.json"
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"📋 Full results saved to: {output_file}")
                
            else:
                click.echo("❌ ABN lookup failed", err=True)
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            raise click.Abort()
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.option('--count', '-c', default=1, help='Number of synthetic companies to generate')
@click.option('--industry', help='Specific industry for generated companies')
@click.option('--state', help='Australian state for generated companies')
@click.option('--output-dir', '-o', default='output_pdfs', help='Output directory for PDFs')
def generate(count, industry, state, output_dir):
    """Generate synthetic liquidation documents automatically
    
    Example:
    python main.py generate --count 5 --industry "Technology Services" --state NSW
    """
    async def run():
        await initialize_supervisor()
        
        try:
            click.echo(f"🎲 Generating {count} synthetic liquidation scenarios...")
            
            if industry:
                click.echo(f"🏭 Industry: {industry}")
            if state:
                click.echo(f"📍 State: {state}")
            
            successful = 0
            failed = 0
            
            for i in range(count):
                try:
                    # Generate synthetic prompt
                    prompt_parts = ["Generate liquidation documents for"]
                    
                    if industry:
                        prompt_parts.append(f"a {industry} company")
                    else:
                        prompt_parts.append("a company")
                    
                    if state:
                        prompt_parts.append(f"in {state}")
                    
                    prompt_parts.append("with financial difficulties")
                    
                    prompt = " ".join(prompt_parts)
                    
                    click.echo(f"  📝 Generating scenario {i+1}/{count}...")
                    
                    result = await supervisor.generate_from_prompt(prompt)
                    
                    if result['success']:
                        company_name = result['company_data']['company_name']
                        doc_count = len([d for d in result['documents'] if d['success']])
                        click.echo(f"  ✅ {company_name}: {doc_count} documents")
                        successful += 1
                    else:
                        click.echo(f"  ❌ Scenario {i+1} failed")
                        failed += 1
                        
                except Exception as e:
                    click.echo(f"  ❌ Scenario {i+1} error: {e}")
                    failed += 1
            
            click.echo(f"📈 Generation complete: {successful} successful, {failed} failed")
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            raise click.Abort()
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
def status():
    """Check system status and agent health"""
    async def run():
        await initialize_supervisor()
        
        try:
            # Get agent status
            agents_info = await supervisor.list_agents()
            health = await supervisor.health_check()
            
            click.echo("🏥 System Health Check")
            click.echo("=" * 50)
            
            # Supervisor status
            supervisor_health = health['supervisor']
            status_icon = "✅" if supervisor_health['status'] == 'healthy' else "⚠️" if supervisor_health['status'] == 'degraded' else "❌"
            click.echo(f"{status_icon} Supervisor: {supervisor_health['status']}")
            if supervisor_health['issues']:
                for issue in supervisor_health['issues']:
                    click.echo(f"   • {issue}")
            
            click.echo("\n🤖 Agent Status")
            click.echo("-" * 30)
            
            for agent_name, agent_info in agents_info['agents'].items():
                agent_health = health['agents'][agent_name]
                status_icon = "✅" if agent_health['status'] == 'healthy' else "⚠️" if agent_health['status'] == 'degraded' else "❌"
                
                status = agent_info['status']
                click.echo(f"{status_icon} {agent_name.replace('_', ' ').title()}: {agent_health['status']}")
                click.echo(f"   Capabilities: {', '.join(agent_info['capabilities'])}")
                click.echo(f"   Queue: {status['queued_tasks']} tasks, Completed: {status['completed_tasks']}")
                
                if agent_health['issues']:
                    for issue in agent_health['issues']:
                        click.echo(f"   ⚠️ {issue}")
                click.echo()
            
            # Check PDF engines
            if supervisor.pdf_generation_agent:
                engines = supervisor.pdf_generation_agent.get_available_engines()
                click.echo(f"📄 Available PDF Engines: {', '.join(engines) if engines else 'None'}")
            
            # Check OpenAI
            if supervisor.llm_generation_agent.client:
                click.echo("🧠 OpenAI API: Connected")
            else:
                click.echo("🧠 OpenAI API: Not configured (using fallback)")
                
        except Exception as e:
            click.echo(f"❌ Status check failed: {e}", err=True)
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.option('--templates-dir', default='templates', help='Templates directory')
def templates():
    """List available document templates"""
    async def run():
        await initialize_supervisor()
        
        try:
            templates_result = await supervisor.template_engine_agent.add_task("list_templates", {})
            templates_task = await supervisor.template_engine_agent.execute_next_task()
            
            if templates_task and templates_task.result:
                templates_list = templates_task.result['templates']
                
                click.echo("📄 Available Document Templates")
                click.echo("=" * 40)
                
                for template in templates_list:
                    status_icon = "✅" if template['valid'] else "❌"
                    size_kb = template['size'] / 1024
                    click.echo(f"{status_icon} {template['name']} ({size_kb:.1f} KB)")
                    
                    if not template['valid']:
                        click.echo(f"   ❌ Error: {template.get('error', 'Unknown error')}")
                
                click.echo(f"\nTotal: {len(templates_list)} templates")
            else:
                click.echo("❌ Failed to list templates")
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.option('--days', default=7, help='Delete files older than N days')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
def cleanup(days, dry_run):
    """Clean up old generated PDF files"""
    async def run():
        await initialize_supervisor()
        
        try:
            if dry_run:
                click.echo(f"🧹 Dry run: Would delete PDF files older than {days} days")
                # For dry run, we'd need to implement a separate check method
                click.echo("   (Dry run not fully implemented)")
            else:
                click.echo(f"🧹 Cleaning up PDF files older than {days} days...")
                
                result = supervisor.pdf_generation_agent.cleanup_old_files(days)
                
                if result['success']:
                    click.echo(f"✅ Deleted {result['deleted_count']} files")
                    for file in result['deleted_files']:
                        click.echo(f"   • {file}")
                else:
                    click.echo(f"❌ Cleanup failed: {result['error']}")
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
def setup():
    """Setup environment and check dependencies"""
    click.echo("🔧 Liquidation Document Generator Setup")
    click.echo("=" * 40)
    
    # Check Python version
    import sys
    click.echo(f"🐍 Python: {sys.version}")
    
    # Check dependencies
    dependencies = [
        ('pandas', 'CSV processing'),
        ('jinja2', 'Template rendering'),
        ('weasyprint', 'PDF generation (HTML to PDF)'),
        ('reportlab', 'PDF generation (Direct)'),
        ('openai', 'LLM integration'),
        ('faker', 'Synthetic data generation'),
        ('click', 'CLI interface'),
        ('aiohttp', 'HTTP requests')
    ]
    
    click.echo("\n📦 Dependencies:")
    for package, description in dependencies:
        try:
            __import__(package)
            click.echo(f"✅ {package}: Available ({description})")
        except ImportError:
            click.echo(f"❌ {package}: Missing ({description})")
    
    # Check environment variables
    click.echo("\n🔑 Environment Variables:")
    env_vars = [
        ('OPENAI_API_KEY', 'OpenAI API access (optional)'),
        ('ABN_API_KEY', 'ABN Lookup API access (optional)')
    ]
    
    for var, description in env_vars:
        value = os.getenv(var)
        if value:
            masked = f"{value[:8]}..." if len(value) > 8 else "***"
            click.echo(f"✅ {var}: Set ({masked}) - {description}")
        else:
            click.echo(f"⚠️ {var}: Not set - {description}")
    
    # Check directories
    click.echo("\n📁 Directories:")
    directories = ['templates', 'output_pdfs', 'data']
    for directory in directories:
        path = Path(directory)
        if path.exists():
            click.echo(f"✅ {directory}/: Exists")
        else:
            click.echo(f"⚠️ {directory}/: Will be created")
            path.mkdir(exist_ok=True)
    
    click.echo("\n✅ Setup complete! You can now run:")
    click.echo("   python main.py prompt \"Generate docs for a tech startup with cash flow issues\"")
    click.echo("   python main.py status")

if __name__ == '__main__':
    cli() 